"""
POST /api/interview — exact evaluator contract endpoint.

Implements the state machine routing:
  NEW             → sessionId + candidate  → initialize session, return welcome + Q1
  ACTIVE          → sessionId + message    → evaluate answer, return next question
  READY_TO_FINISH → after answer when gates met → return done=true + feedback
  COMPLETED       → further messages       → idempotent final result
  UNKNOWN_SESSION → message without session → HTTP 400
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession

from app.models.candidate import CandidateProfile
from app.models.interview import (
    InterviewRequest,
    InterviewResponse,
    InterviewSession,
    SessionStatus,
    DifficultyLevel,
    QuestionKind,
    InterviewTurn,
)
from app.models.feedback import InterviewFeedback
from app.core.data_loader import get_curriculum_day
from app.core.config import (
    WEIGHT_COMPLETION,
    WEIGHT_FIRST_TRY,
    WEIGHT_CONSISTENCY,
    TOTAL_CURRICULUM_DAYS,
)
from app.core.database import SessionLocal, InterviewSessionModel, InterviewTurnModel
from app.services.candidate_analyzer import get_eligible_curriculum_days
from app.services.answer_evaluator import evaluate_answer
from app.services.followup_controller import adapt_follow_up
from app.services.question_generator import generate_question
from app.models.interview import FollowUpType
logger = logging.getLogger(__name__)

router = APIRouter()


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Helper: compute skill prior from candidate signals
# ---------------------------------------------------------------------------

def _compute_skill_prior(candidate: CandidateProfile) -> float:
    signals = candidate.signals
    completion = signals.missionsCompleted / TOTAL_CURRICULUM_DAYS
    first_try = signals.missionsFirstTry / max(signals.missionsCompleted, 1)
    consistency = signals.commitDays / TOTAL_CURRICULUM_DAYS
    return round(
        WEIGHT_COMPLETION * completion
        + WEIGHT_FIRST_TRY * first_try
        + WEIGHT_CONSISTENCY * consistency,
        4,
    )


def _difficulty_from_prior(prior: float) -> DifficultyLevel:
    if prior < 0.50:
        return DifficultyLevel.FOUNDATION
    elif prior < 0.75:
        return DifficultyLevel.APPLIED
    else:
        return DifficultyLevel.SYSTEMS


# ---------------------------------------------------------------------------
# Helper: build initial interview plan
# ---------------------------------------------------------------------------

def _build_interview_plan(candidate_profile_dict: dict) -> list[int]:
    """Select curriculum days to cover in the interview using pure dict function."""
    eligible = get_eligible_curriculum_days(candidate_profile_dict)
    if not eligible:
        return []

    # Group eligible days by module for diversity
    curriculum_modules: dict[int, list[int]] = {}
    for day in eligible:
        cd = get_curriculum_day(day)
        if cd:
            curriculum_modules.setdefault(cd.module_no, []).append(day)

    # Pick one day from each module first (for diversity), then fill
    planned: list[int] = []
    for module_no in sorted(curriculum_modules.keys()):
        days_in_module = curriculum_modules[module_no]
        planned.append(days_in_module[0])

    # If we still don't have enough, add remaining eligible days
    for day in eligible:
        if day not in planned:
            planned.append(day)

    return planned


# ---------------------------------------------------------------------------
# Helper: generate mock welcome message
# ---------------------------------------------------------------------------

def _generate_welcome(candidate_name: str, candidate_role: str, planned_days: list[int]) -> str:
    role = candidate_role or "professional"

    # Pick the first planned day
    if planned_days:
        first_day = planned_days[0]
        cd = get_curriculum_day(first_day)
        topic = cd.title if cd else f"Day {first_day}"
        objectives = cd.objectives if cd else []
    else:
        topic = "your learning journey"
        objectives = []

    welcome = (
        f"Welcome, {candidate_name}! I'm excited to learn about your experience as "
        f"a {role} and explore what you've built during the AI Builder program. "
        f"I'll be asking you questions across several topics from your curriculum "
        f"to understand your strengths and where you might grow next.\n\n"
        f"Let's start with **{topic}**."
    )

    if objectives:
        question = (
            f" Specifically, {objectives[0].lower()} — "
            f"can you walk me through how you approached this and what you learned?"
        )
    else:
        question = " Can you tell me about your experience with this topic?"

    return welcome + question


# ---------------------------------------------------------------------------
# Helper: map DB model to Pydantic Session Model
# ---------------------------------------------------------------------------

def _db_to_pydantic_session(db_session: InterviewSessionModel) -> InterviewSession:
    """Helper to reconstruct the Pydantic session for computing gates."""
    candidate = CandidateProfile.model_validate(db_session.candidate_snapshot)
    
    # We need to reconstruct planned_days, etc.
    # To keep this mock state machine working, we recompute planned_days.
    planned_days = _build_interview_plan(db_session.candidate_snapshot)
    
    # Compute skill prior
    skill_prior = _compute_skill_prior(candidate)
    
    turns = [
        InterviewTurn(
            turn_no=t.turn_no,
            role=t.role,
            content=t.content,
            curriculum_day=t.curriculum_day,
            # we default to anchor for now
            question_kind=QuestionKind.ANCHOR if t.role == "INTERVIEWER" else None
        ) for t in sorted(db_session.turns, key=lambda x: x.turn_no)
    ]
    
    # Simple state recovery for the mock evaluator
    # Assuming standard alternating turns:
    current_day_index = len(db_session.covered_days)
    if not db_session.covered_days and planned_days:
        current_day_index = 1

    return InterviewSession(
        session_id=db_session.session_id,
        candidate_snapshot=candidate,
        status=SessionStatus(db_session.status),
        skill_prior=skill_prior,
        current_difficulty=_difficulty_from_prior(skill_prior),
        planned_days=planned_days,
        question_count=db_session.question_count,
        follow_up_count=db_session.question_count // 3,
        covered_days=db_session.covered_days,
        current_day_index=current_day_index,
        turns=turns,
        # Mock final feedback if completed
        final_feedback=InterviewFeedback(
            summary=f"{candidate.member.name} completed the interview.",
            strengths=["Good"],
            gaps=["None"],
            next=["Next steps"]
        ) if db_session.status == "COMPLETED" else None
    )


# ═══════════════════════════════════════════════════════════════════════════
# THE ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/api/interview", response_model=InterviewResponse)
async def interview(
    request: InterviewRequest,
    db: DBSession = Depends(get_db)
) -> InterviewResponse:
    """POST /api/interview — the single evaluator contract endpoint."""
    session_id = request.sessionId

    # Check if session exists in DB
    db_session = db.query(InterviewSessionModel).filter(InterviewSessionModel.session_id == session_id).first()

    # ── CASE 1: Start request (sessionId + candidate) ──────────────────
    if request.is_start:
        if db_session:
            if db_session.status == SessionStatus.COMPLETED.value:
                return InterviewResponse(
                    reply="This interview has already been completed.",
                    done=True,
                    feedback=InterviewFeedback(
                        summary="Interview completed.",
                        strengths=["Good"], gaps=["None"], next=["Next steps"]
                    )
                )
            raise HTTPException(
                status_code=400,
                detail=f"Session '{session_id}' is already active.",
            )

        candidate = request.candidate
        candidate_dict = candidate.model_dump(mode="json")
        
        # Build interview plan and eligible days using the candidate analyzer
        planned_days = _build_interview_plan(candidate_dict)
        
        # Initial covered day
        covered_days = [planned_days[0]] if planned_days else []

        # Create session in DB
        db_session = InterviewSessionModel(
            session_id=session_id,
            candidate_snapshot=candidate_dict,
            question_count=1,
            covered_days=covered_days,
            status=SessionStatus.ACTIVE.value
        )
        db.add(db_session)
        
        # Generate welcome
        welcome = _generate_welcome(candidate.member.name, candidate.member.jobRole, planned_days)

        # Create interviewer turn in DB
        first_turn = InterviewTurnModel(
            session_id=session_id,
            turn_no=1,
            role="INTERVIEWER",
            content=welcome,
            curriculum_day=planned_days[0] if planned_days else None
        )
        db.add(first_turn)
        db.commit()

        return InterviewResponse(reply=welcome, done=False)

    # ── CASE 2: Turn request (sessionId + message) ─────────────────────
    if db_session is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown session '{session_id}'. Start an interview by sending a 'candidate' object first.",
        )

    if db_session.status == SessionStatus.COMPLETED.value:
        return InterviewResponse(
            reply="This interview has already been completed.",
            done=True,
            feedback=InterviewFeedback(
                summary="Interview completed.",
                strengths=["Good"], gaps=["None"], next=["Next steps"]
            )
        )

    # Fetch candidate info for plan
    candidate_dict = db_session.candidate_snapshot
    planned_days = _build_interview_plan(candidate_dict)
    
    # Calculate current turn_no
    turn_no = len(db_session.turns) + 1
    last_interviewer_turn = next((t for t in reversed(db_session.turns) if t.role == "INTERVIEWER"), None)
    current_day = last_interviewer_turn.curriculum_day if last_interviewer_turn else None

    # ── LLM EVALUATION ──
    last_interviewer_content = last_interviewer_turn.content if last_interviewer_turn else ""
    current_cd = get_curriculum_day(current_day) if current_day else None
    objectives = current_cd.objectives if current_cd else []
    tools = current_cd.tools if current_cd else []
    
    evaluation = evaluate_answer(
        candidate_answer=request.message,
        context_summary="",  # Mock context summary
        curriculum_objectives=objectives,
        curriculum_tools=tools
    )
    evaluation = adapt_follow_up(evaluation)

    # Insert Candidate Turn with evaluation
    candidate_turn = InterviewTurnModel(
        session_id=session_id,
        turn_no=turn_no,
        role="CANDIDATE",
        content=request.message,
        curriculum_day=current_day
    )
    db.add(candidate_turn)

    # Update state
    db_session.question_count += 1
    
    # Determine next topic
    if evaluation.follow_up_needed:
        next_day = current_day
        question_kind = QuestionKind.FOLLOW_UP_CLARIFY if evaluation.follow_up_type == FollowUpType.CLARIFY else QuestionKind.FOLLOW_UP_SCENARIO
        follow_up_focus = evaluation.follow_up_focus
    else:
        next_day_index = len(db_session.covered_days)
        if next_day_index < len(planned_days):
            next_day = planned_days[next_day_index]
            db_session.covered_days = db_session.covered_days + [next_day]
            db.add(db_session)
        else:
            next_day = None
        question_kind = QuestionKind.ANCHOR
        follow_up_focus = ""

    # Reconstruct Pydantic session for gates evaluation
    pydantic_session = _db_to_pydantic_session(db_session)
    
    # Hack to increment follow_up_count for the mock if we actually did one
    if evaluation.follow_up_needed:
        pydantic_session.follow_up_count += 1

    # Check hard gates
    if pydantic_session.gates_met:
        db_session.status = SessionStatus.COMPLETED.value
        db.commit()

        candidate_name = candidate_dict.get("member", {}).get("name", "Candidate")
        feedback = InterviewFeedback(
            summary=(
                f"{candidate_name} demonstrated understanding across "
                f"{len(db_session.covered_days)} curriculum areas with "
                f"{db_session.question_count} questions answered."
            ),
            strengths=[
                "Engaged thoughtfully with interview questions",
                "Showed familiarity with core curriculum concepts",
            ],
            gaps=[
                "Some responses lacked implementation-level depth",
            ],
            next=[
                "Practice building end-to-end projects",
                "Review advanced topics for deeper understanding",
            ],
        )
        return InterviewResponse(
            reply="Thank you for completing this interview. Here is your feedback.",
            done=True,
            feedback=feedback,
        )

    # ── GENERATE NEXT QUESTION ──
    if next_day:
        cd = get_curriculum_day(next_day)
        n_objectives = cd.objectives if cd else []
        n_tools = cd.tools if cd else []
    else:
        n_objectives, n_tools = [], []
        next_day = current_day or 1

    candidate_role = candidate_dict.get("member", {}).get("jobRole", "professional")
    
    generated_q = generate_question(
        day=next_day,
        objectives=n_objectives,
        tools=n_tools,
        difficulty=evaluation.recommended_next_difficulty if hasattr(evaluation, "recommended_next_difficulty") else DifficultyLevel.APPLIED,
        question_kind=question_kind,
        candidate_role=candidate_role,
        context_summary="",
        follow_up_focus=follow_up_focus
    )
    next_question = generated_q.question_text

    # Insert Interviewer Turn
    interviewer_turn = InterviewTurnModel(
        session_id=session_id,
        turn_no=turn_no + 1,
        role="INTERVIEWER",
        content=next_question,
        curriculum_day=next_day
    )
    db.add(interviewer_turn)
    db.commit()

    return InterviewResponse(reply=next_question, done=False)
