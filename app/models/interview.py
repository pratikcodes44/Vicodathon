"""
Interview request / response and internal session-state Pydantic models.

This file contains:
  1. **API contract models** — the exact request/response shapes the evaluator
     expects for ``POST /api/interview``.
  2. **Internal state models** — persisted in SQLite to enforce the deterministic
     state machine (topic eligibility, hard minimums, follow-up tracking).
  3. **LLM structured-output models** — the JSON schemas we require from the LLM
     for answer evaluation and question generation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from app.models.candidate import CandidateProfile
from app.models.feedback import InterviewFeedback


# ═══════════════════════════════════════════════════════════════════════════
# 1. API CONTRACT MODELS
# ═══════════════════════════════════════════════════════════════════════════

class InterviewRequest(BaseModel):
    """Inbound payload for ``POST /api/interview``.

    The evaluator sends ONE of two shapes:
      • **Start turn**: ``sessionId`` + ``candidate`` (no ``message``)
      • **Subsequent turn**: ``sessionId`` + ``message`` (no ``candidate``)

    Both fields are Optional at the Pydantic level; mutual exclusivity is
    enforced by the ``validate_turn_type`` validator.
    """

    model_config = {"extra": "allow"}

    sessionId: str = Field(
        ..., min_length=1, description="Unique session identifier from the evaluator"
    )
    candidate: Optional[CandidateProfile] = Field(
        default=None,
        description="Candidate profile; present only on the first (start) request",
    )
    message: Optional[str] = Field(
        default=None,
        description="Candidate's answer; present on subsequent (turn) requests",
    )

    @model_validator(mode="after")
    def validate_turn_type(self) -> "InterviewRequest":
        """Ensure exactly one of ``candidate`` or ``message`` is present."""
        has_candidate = self.candidate is not None
        has_message = self.message is not None

        if has_candidate and has_message:
            raise ValueError(
                "Request must contain either 'candidate' (start) or 'message' (turn), not both."
            )
        if not has_candidate and not has_message:
            raise ValueError(
                "Request must contain either 'candidate' (start) or 'message' (turn)."
            )
        return self

    @property
    def is_start(self) -> bool:
        """True when this is the first request that initializes the session."""
        return self.candidate is not None


class InterviewResponse(BaseModel):
    """Outbound payload for ``POST /api/interview``.

    Every response carries ``reply`` and ``done``.  When ``done`` is True
    the ``feedback`` object is mandatory and must match the evaluator's
    exact schema.
    """

    reply: str = Field(
        ..., min_length=1, description="Interviewer message or question"
    )
    done: bool = Field(
        default=False,
        description="True only when the interview is complete",
    )
    feedback: Optional[InterviewFeedback] = Field(
        default=None,
        description="Present only when done=true; validated against the contract",
    )

    @model_validator(mode="after")
    def feedback_required_when_done(self) -> "InterviewResponse":
        """If ``done`` is True, ``feedback`` must be present and complete."""
        if self.done and self.feedback is None:
            raise ValueError("feedback is required when done=true")
        return self


# ═══════════════════════════════════════════════════════════════════════════
# 2. INTERNAL STATE MACHINE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class SessionStatus(str, Enum):
    """Deterministic session states — enforced in Python, not the LLM."""

    NEW = "NEW"
    ACTIVE = "ACTIVE"
    READY_TO_FINISH = "READY_TO_FINISH"
    COMPLETED = "COMPLETED"


class DifficultyLevel(str, Enum):
    """Interview difficulty tiers derived from the adaptive difficulty formula."""

    FOUNDATION = "FOUNDATION"
    APPLIED = "APPLIED"
    SYSTEMS = "SYSTEMS"


class QuestionKind(str, Enum):
    """Categorizes whether a turn is an anchor question or a follow-up."""

    ANCHOR = "ANCHOR"
    FOLLOW_UP_CLARIFY = "FOLLOW_UP_CLARIFY"
    FOLLOW_UP_DEEPEN = "FOLLOW_UP_DEEPEN"
    FOLLOW_UP_SCENARIO = "FOLLOW_UP_SCENARIO"


class InterviewTurn(BaseModel):
    """One turn in the interview transcript, persisted for evidence and replay."""

    turn_no: int = Field(..., ge=1, description="1-indexed turn number")
    role: str = Field(
        ...,
        pattern=r"^(INTERVIEWER|CANDIDATE)$",
        description="Who produced this turn",
    )
    content: str = Field(..., description="The text of this turn")
    curriculum_day: Optional[int] = Field(
        default=None,
        description="Which curriculum day this question targets (interviewer turns only)",
    )
    question_kind: Optional[QuestionKind] = Field(
        default=None,
        description="Type of question (interviewer turns only)",
    )
    score: Optional[float] = Field(
        default=None,
        ge=0,
        le=4,
        description="Answer score from the evaluator (candidate turns only)",
    )
    evaluation: Optional[dict[str, Any]] = Field(
        default=None,
        description="Full structured evaluation JSON (candidate turns only)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of this turn",
    )


class InterviewSession(BaseModel):
    """Complete internal session state, persisted to SQLite.

    This is the single source of truth for the deterministic state machine.
    The LLM never controls transitions — Python code reads this state,
    enforces hard gates, and writes back after each turn.
    """

    session_id: str = Field(
        ..., description="Evaluator-supplied session ID"
    )
    candidate_snapshot: CandidateProfile = Field(
        ..., description="Full candidate profile snapshot from the start request"
    )
    status: SessionStatus = Field(
        default=SessionStatus.ACTIVE,
        description="Current state-machine status",
    )

    # ---- interview progress counters (hard gates) ----
    question_count: int = Field(
        default=0,
        ge=0,
        description="Total questions asked (anchor + follow-up)",
    )
    follow_up_count: int = Field(
        default=0,
        ge=0,
        description="Number of response-driven follow-ups asked",
    )
    covered_days: list[int] = Field(
        default_factory=list,
        description="Distinct curriculum days covered by questions so far",
    )

    # ---- adaptive difficulty ----
    skill_prior: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Computed skill prior from candidate signals (0.0-1.0)",
    )
    current_difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.APPLIED,
        description="Current adaptive difficulty level",
    )

    # ---- interview plan ----
    planned_days: list[int] = Field(
        default_factory=list,
        description="Pre-planned curriculum days to cover in this interview",
    )
    current_day_index: int = Field(
        default=0,
        ge=0,
        description="Index into planned_days for the current topic",
    )

    # ---- context for LLM ----
    context_summary: str = Field(
        default="",
        description="Running 150-250 word summary of interview so far",
    )
    turns: list[InterviewTurn] = Field(
        default_factory=list,
        description="Full ordered transcript of interview turns",
    )

    # ---- last question metadata (for evaluating the answer) ----
    last_question_day: Optional[int] = Field(
        default=None,
        description="Curriculum day of the most recent question",
    )
    last_question_kind: Optional[QuestionKind] = Field(
        default=None,
        description="Kind of the most recent question",
    )

    # ---- timestamps ----
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Session start timestamp",
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Session completion timestamp (set when done)",
    )

    # ---- stored final feedback ----
    final_feedback: Optional[InterviewFeedback] = Field(
        default=None,
        description="Persisted feedback for idempotent re-retrieval",
    )

    # ---- hard gate helpers ------------------------------------------------

    @property
    def distinct_days_covered(self) -> int:
        """Number of distinct curriculum days covered so far."""
        return len(set(self.covered_days))

    @property
    def has_follow_up(self) -> bool:
        """True if at least one response-driven follow-up has been asked."""
        return self.follow_up_count >= 1

    @property
    def gates_met(self) -> bool:
        """True when ALL hard completion gates are satisfied.

        Gates:
          1. question_count >= 8
          2. distinct curriculum days covered >= 4
          3. At least one response-driven follow-up occurred
        """
        return (
            self.question_count >= 8
            and self.distinct_days_covered >= 4
            and self.has_follow_up
        )


# ═══════════════════════════════════════════════════════════════════════════
# 3. LLM STRUCTURED OUTPUT MODELS
# ═══════════════════════════════════════════════════════════════════════════

class FollowUpType(str, Enum):
    """Follow-up action category from the answer evaluator."""

    CLARIFY = "CLARIFY"
    DEEPEN = "DEEPEN"
    SCENARIO = "SCENARIO"
    NONE = "NONE"


class AnswerEvaluation(BaseModel):
    """Structured JSON the LLM must produce when scoring a candidate answer.

    Validated with Pydantic before any state transition occurs.
    Temperature should be low (0.1-0.3) for this call.
    """

    score: int = Field(
        ...,
        ge=0,
        le=4,
        description="0-4 rubric score",
    )
    correctness: str = Field(
        ...,
        description="Assessment of factual correctness",
    )
    depth: str = Field(
        ...,
        description="Assessment of technical depth",
    )
    communication: str = Field(
        ...,
        description="Assessment of clarity and communication",
    )
    misconceptions: list[str] = Field(
        default_factory=list,
        description="Any misconceptions detected in the answer",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Specific phrases/claims from the candidate answer (paraphrased)",
    )
    follow_up_needed: bool = Field(
        ...,
        description="Whether a follow-up question is warranted",
    )
    follow_up_type: FollowUpType = Field(
        ...,
        description="Category of follow-up: CLARIFY | DEEPEN | SCENARIO | NONE",
    )
    follow_up_focus: str = Field(
        default="",
        description="Specific topic/concept the follow-up should target",
    )
    recommended_next_difficulty: DifficultyLevel = Field(
        ...,
        description="Recommended difficulty for the next question",
    )


class GeneratedQuestion(BaseModel):
    """Structured JSON the LLM must produce when generating a question.

    The orchestrator fills in ``curriculum_day``, ``difficulty``, and
    ``candidate_role`` before sending the prompt; the LLM returns the
    question text and metadata.
    """

    question_text: str = Field(
        ...,
        min_length=10,
        description="The interview question to ask the candidate",
    )
    curriculum_day: int = Field(
        ...,
        ge=1,
        le=31,
        description="Which curriculum day this question targets",
    )
    objective_focus: str = Field(
        ...,
        description="Which learning objective this question probes",
    )
    difficulty: DifficultyLevel = Field(
        ...,
        description="Difficulty tier of this question",
    )
    question_kind: QuestionKind = Field(
        default=QuestionKind.ANCHOR,
        description="Whether this is an anchor or follow-up question",
    )


class GeneratedFeedback(BaseModel):
    """Structured JSON the LLM produces for the final feedback composition.

    Validated against the contract ``InterviewFeedback`` schema before
    being returned to the evaluator.
    """

    summary: str = Field(
        ...,
        min_length=1,
        description="Narrative performance summary",
    )
    strengths: list[str] = Field(
        ...,
        min_length=1,
        description="Evidence-backed strengths",
    )
    gaps: list[str] = Field(
        ...,
        min_length=1,
        description="Identified knowledge gaps",
    )
    next: list[str] = Field(
        ...,
        min_length=1,
        description="Recommended next learning steps",
    )

    def to_feedback(self) -> InterviewFeedback:
        """Convert to the exact API contract feedback model."""
        return InterviewFeedback(
            summary=self.summary,
            strengths=self.strengths,
            gaps=self.gaps,
            next=self.next,
        )
