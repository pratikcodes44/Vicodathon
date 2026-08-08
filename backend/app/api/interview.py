from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
import json

from app.core.supabase import supabase
from app.services.answer_evaluator import evaluate_answer
from app.services.followup_controller import adapt_follow_up
from app.services.question_generator import generate_question
from app.services.feedback_composer import compose_final_feedback
from app.models.interview import DifficultyLevel, QuestionKind
from app.models.interview import InterviewTurn

router = APIRouter()

class InterviewRequest(BaseModel):
    sessionId: str
    message: str | None = None
    is_start: bool = False
    candidate: Any | None = None

class InterviewResponse(BaseModel):
    reply: str
    done: bool = False
    feedback: Any | None = None

@router.post("/api/interview", response_model=InterviewResponse)
async def interview(request: InterviewRequest):
    session_id = request.sessionId

    # Fetch session from Supabase
    res = supabase.table("interview_sessions").select("*, candidates(*)").eq("id", session_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Session not found in Supabase")
    
    session = res.data[0]
    candidate = session["candidates"]

    if session["status"] == "completed":
        return InterviewResponse(reply="Interview already completed.", done=True)

    # Calculate current turn and history
    chat_res = supabase.table("chat_messages").select("*").eq("session_id", session_id).order("created_at").execute()
    messages = chat_res.data
    
    # We define interview length
    MAX_TURNS = 4
    current_turn = session.get("current_turn", 1)

    # 1. Handle Candidate's Message
    if request.message and not request.is_start:
        pass # Assuming frontend inserted it

    # 2. Evaluate if we should finish
    if current_turn >= MAX_TURNS and not request.is_start:
        # Finish interview
        turns = []
        for i, m in enumerate(messages):
            turns.append(InterviewTurn(
                turn_no=i,
                role="INTERVIEWER" if m["sender"] == "interviewer" else "CANDIDATE",
                content=m["content"],
                curriculum_day=1,
                question_kind=None
            ))

        generated_feedback = await compose_final_feedback(
            candidate_role=candidate.get("role", "professional"),
            turns=turns
        )
        
        fb_dict = generated_feedback.model_dump()
        
        # Insert scorecard
        supabase.table("scorecards").insert({
            "session_id": session_id,
            "overall_score": 8,
            "communication_score": 8.5,
            "technical_score": 7.5,
            "problem_solving_score": 8.0,
            "detailed_feedback": fb_dict
        }).execute()

        # Update session
        supabase.table("interview_sessions").update({"status": "completed"}).eq("id", session_id).execute()

        return InterviewResponse(
            reply="Thank you for your time. The interview is now complete.",
            done=True,
            feedback=fb_dict
        )

    # 3. Generate Next Question
    last_q = next((m["content"] for m in reversed(messages) if m["sender"] == "interviewer"), "")
    
    generated_q = await generate_question(
        day=current_turn,
        title="General Topic",
        objectives=[],
        tools=[],
        difficulty=DifficultyLevel.APPLIED,
        question_kind=QuestionKind.ANCHOR,
        candidate_role=candidate.get("role", "professional"),
        last_question=last_q,
        last_answer=request.message or "",
        follow_up_focus=""
    )
    
    next_question = generated_q.question_text

    # Log interviewer turn
    supabase.table("chat_messages").insert({
        "session_id": session_id,
        "sender": "interviewer",
        "content": next_question
    }).execute()

    # Update session turn
    supabase.table("interview_sessions").update({
        "current_turn": current_turn + 1
    }).eq("id", session_id).execute()

    return InterviewResponse(reply=next_question, done=False)
