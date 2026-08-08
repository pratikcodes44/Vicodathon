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
import json
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
from app.core.data_loader import get_curriculum_day, get_candidates
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
from app.services.feedback_composer import compose_final_feedback
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

    plan = planned[:4]
    if not plan or len(plan) == 0:
        plan = [7, 10, 13, 22]

    return plan


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
    candidate_dict = json.loads(db_session.candidate_snapshot) if isinstance(db_session.candidate_snapshot, str) else db_session.candidate_snapshot
    candidate = CandidateProfile.model_validate(candidate_dict)
    
    # We need to reconstruct planned_days, etc.
    # To keep this mock state machine working, we recompute planned_days.
    planned_days = _build_interview_plan(candidate_dict)
    
    session_plan = json.loads(db_session.plan) if isinstance(db_session.plan, str) else db_session.plan
    
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
    
    # The remaining simple state recovery using the new queue logic is handled dynamically.

    return InterviewSession(
        session_id=db_session.session_id,
        candidate_snapshot=candidate,
        status=SessionStatus(db_session.status),
        skill_prior=skill_prior,
        current_difficulty=_difficulty_from_prior(skill_prior),
        plan=session_plan,
        plan_index=db_session.plan_index,
        turns_in_current_day=db_session.turns_in_current_day,
        total_questions=db_session.total_questions,
        score_communication=db_session.score_communication,
        score_technical=db_session.score_technical,
        score_problem_solving=db_session.score_problem_solving,
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
        
        # Create session in DB
        db_session = InterviewSessionModel(
            session_id=session_id,
            candidate_snapshot=candidate_dict,
            plan=planned_days,
            plan_index=0,
            turns_in_current_day=0,
            total_questions=0,
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
    candidate_dict = json.loads(db_session.candidate_snapshot) if isinstance(db_session.candidate_snapshot, str) else db_session.candidate_snapshot
    
    # We don't actually need to re-plan, we can use the existing plan in the session
    session_plan = json.loads(db_session.plan) if isinstance(db_session.plan, str) else db_session.plan
    
    # Calculate current turn_no
    turn_no = len(db_session.turns) + 1
    last_interviewer_turn = next((t for t in reversed(db_session.turns) if t.role == "INTERVIEWER"), None)
    current_day = last_interviewer_turn.curriculum_day if last_interviewer_turn else None

    # ── LLM EVALUATION ──
    last_interviewer_content = last_interviewer_turn.content if last_interviewer_turn else ""
    current_cd = get_curriculum_day(current_day) if current_day else None
    objectives = current_cd.objectives if current_cd else []
    tools = current_cd.tools if current_cd else []
    
    evaluation = await evaluate_answer(
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
    db_session.total_questions += 1
    db_session.turns_in_current_day += 1
    db_session.score_communication += evaluation.score_communication
    db_session.score_technical += evaluation.score_technical
    db_session.score_problem_solving += evaluation.score_problem_solving
    
    # State Machine Transition Rules
    if evaluation.score <= 1 and db_session.turns_in_current_day == 1:
        # Stay on current day for a follow-up
        next_day = current_day
        question_kind = QuestionKind.FOLLOW_UP_CLARIFY
        follow_up_focus = evaluation.follow_up_focus
    else:
        # Advance to next day
        db_session.plan_index += 1
        db_session.turns_in_current_day = 0
        
        if db_session.plan_index < len(session_plan):
            next_day = session_plan[db_session.plan_index]
        else:
            next_day = None # Will trigger completion or fallback
            
        question_kind = QuestionKind.ANCHOR
        follow_up_focus = ""

    db.add(db_session)

    # Reconstruct Pydantic session for gates evaluation
    pydantic_session = _db_to_pydantic_session(db_session)

    # Check hard gates
    if db_session.plan_index >= len(session_plan) or db_session.total_questions >= 8:
        db_session.status = SessionStatus.COMPLETED.value
        db.commit()

        candidate_role = candidate_dict.get("member", {}).get("jobRole", "professional")
        
        # Get all turns to compose feedback
        all_turns = pydantic_session.turns
        
        generated_feedback = await compose_final_feedback(
            candidate_role=candidate_role,
            turns=all_turns
        )
        
        feedback = generated_feedback.to_feedback()
        
        return InterviewResponse(
            reply="Thank you for completing this interview. Here is your feedback.",
            done=True,
            feedback=feedback,
        )

    # ── GENERATE NEXT QUESTION ──
    if next_day:
        cd = get_curriculum_day(next_day)
        n_title = cd.title if cd else f"Day {next_day}"
        n_objectives = cd.objectives if cd else []
        n_tools = cd.tools if cd else []
    else:
        n_title = "General Topic"
        n_objectives, n_tools = [], []
        next_day = current_day or 1

    candidate_role = candidate_dict.get("member", {}).get("jobRole", "professional")
    
    generated_q = await generate_question(
        day=next_day,
        title=n_title,
        objectives=n_objectives,
        tools=n_tools,
        difficulty=evaluation.recommended_next_difficulty if hasattr(evaluation, "recommended_next_difficulty") else DifficultyLevel.APPLIED,
        question_kind=question_kind,
        candidate_role=candidate_role,
        last_question=last_interviewer_content,
        last_answer=request.message,
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


@router.get("/api/candidates")
async def list_candidates():
    """Return a lightweight list of candidates for the frontend."""
    candidates = get_candidates()
    result = []
    for cid, cand in candidates.items():
        status = "Active Interview" if cid == "CAND-018" else "Scheduled"
        result.append({
            "id": cid,
            "name": cand.member.name,
            "jobRole": cand.member.jobRole,
            "status": status
        })
    return result


@router.get("/api/metrics/{session_id}")
async def get_metrics(session_id: str, db: DBSession = Depends(get_db)):
    """Return the current aggregated scores and status for the frontend."""
    db_session = db.query(InterviewSessionModel).filter(InterviewSessionModel.session_id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    candidate_turns = len([t for t in db_session.turns if t.role == "CANDIDATE"])
    max_score = candidate_turns * 4
    
    if db_session.status == SessionStatus.COMPLETED.value:
        summary_status = "Interview Completed"
    elif candidate_turns == 0:
        summary_status = "Not Started"
    else:
        summary_status = f"Interview in progress... (Question {db_session.total_questions})"
        
    return {
        "score_communication": db_session.score_communication,
        "score_technical": db_session.score_technical,
        "score_problem_solving": db_session.score_problem_solving,
        "max_score": max_score,
        "summary_status": summary_status,
        "total_questions": db_session.total_questions,
        "candidate_turns": candidate_turns
    }

