"""
Feedback Composer service — delegates to the unified LLM gateway.
"""
from app.models.interview import GeneratedFeedback, InterviewTurn
from app.services.llm_service import compose_final_feedback as _llm_feedback


def compose_final_feedback(
    candidate_role: str,
    turns: list[InterviewTurn],
) -> GeneratedFeedback:
    """
    Synthesize final interview feedback via the unified LLM gateway.

    The gateway handles multi-provider failover and deterministic fallback
    if all providers fail.
    """
    return _llm_feedback(
        candidate_role=candidate_role,
        turns=turns,
    )
