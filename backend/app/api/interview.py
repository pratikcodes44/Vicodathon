from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
import logging

from app.core.supabase import supabase
from app.services.question_generator import generate_question
from app.services.feedback_composer import compose_final_feedback
from app.models.interview import DifficultyLevel, QuestionKind, InterviewTurn

logger = logging.getLogger(__name__)

router = APIRouter()


class InterviewRequest(BaseModel):
    model_config = {"extra": "allow"}
    sessionId: str
    message: str | None = None
    candidate: Any | None = None


class InterviewResponse(BaseModel):
    reply: str
    done: bool = False
    feedback: Any | None = None


@router.post("/api/interview", response_model=InterviewResponse)
async def interview(request: InterviewRequest):
    session_id = request.sessionId
    logger.info("POST /api/interview — sessionId=%s, message=%s", session_id, bool(request.message))

    # Fetch session from Supabase
    res = supabase.table("interview_sessions").select("*, candidates(*)").eq("id", session_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found in Supabase")

    session = res.data[0]
    candidate = session.get("candidates") or {}
    candidate_role = candidate.get("role", "professional")

    if session["status"] == "completed":
        return InterviewResponse(reply="Interview already completed.", done=True, feedback={"summary": "Already completed."})

    # Fetch chat history
    chat_res = supabase.table("chat_messages").select("*").eq("session_id", session_id).order("created_at").execute()
    messages = chat_res.data or []

    MAX_TURNS = 10
    current_turn = session.get("current_turn", 1)

    # Check if we should finish
    if current_turn >= MAX_TURNS and request.message:
        logger.info("Session %s reached MAX_TURNS (%d), composing final feedback...", session_id, MAX_TURNS)

        # Build turns for feedback composer (turn_no is 1-indexed)
        turns = []
        for i, m in enumerate(messages):
            turns.append(InterviewTurn(
                turn_no=i + 1,  # 1-indexed, required by Pydantic model
                role="INTERVIEWER" if m["sender"] == "interviewer" else "CANDIDATE",
                content=m["content"],
                curriculum_day=1,
                question_kind=None
            ))

        try:
            generated_feedback = await compose_final_feedback(
                candidate_role=candidate_role,
                turns=turns
            )
            fb_dict = generated_feedback.model_dump()
        except Exception as e:
            logger.error("Feedback generation failed: %s", e)
            fb_dict = {
                "summary": f"Interview completed with {len(messages)} exchanges.",
                "strengths": ["Engaged with all questions"],
                "gaps": ["Could not generate detailed analysis"],
                "next": ["Review interview transcript"]
            }

        # Insert scorecard
        try:
            supabase.table("scorecards").insert({
                "session_id": session_id,
                "overall_score": 8,
                "communication_score": 8.5,
                "technical_score": 7.5,
                "problem_solving_score": 8.0,
                "detailed_feedback": fb_dict
            }).execute()
        except Exception as e:
            logger.error("Scorecard insert failed: %s", e)

        # Update session status
        supabase.table("interview_sessions").update({"status": "completed"}).eq("id", session_id).execute()

        return InterviewResponse(
            reply="Thank you for your time. The interview is now complete.",
            done=True,
            feedback=fb_dict
        )

    # Generate Next Question
    last_q = next((m["content"] for m in reversed(messages) if m["sender"] == "interviewer"), "")

    try:
        generated_q = await generate_question(
            day=max(current_turn, 1),
            title="General Topic",
            objectives=[],
            tools=[],
            difficulty=DifficultyLevel.APPLIED,
            question_kind=QuestionKind.ANCHOR,
            candidate_role=candidate_role,
            last_question=last_q,
            last_answer=request.message or "",
            follow_up_focus=""
        )
        next_question = generated_q.question_text
    except Exception as e:
        logger.error("Question generation failed: %s", e)
        next_question = "Tell me more about your experience with this topic and any challenges you faced."

    # Log interviewer turn to Supabase
    try:
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "sender": "interviewer",
            "content": next_question
        }).execute()
    except Exception as e:
        logger.error("Failed to insert chat message: %s", e)

    # Update session turn counter
    supabase.table("interview_sessions").update({
        "current_turn": current_turn + 1
    }).eq("id", session_id).execute()

    return InterviewResponse(reply=next_question, done=False)
