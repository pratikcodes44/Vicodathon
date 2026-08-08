"""
Answer Evaluator service — delegates to the unified LLM gateway.
"""
from app.models.interview import AnswerEvaluation
from app.services.llm_service import evaluate_answer as _llm_evaluate


def evaluate_answer(
    candidate_answer: str,
    context_summary: str,
    curriculum_objectives: list[str],
    curriculum_tools: list[str],
) -> AnswerEvaluation:
    """
    Evaluate a candidate's answer using the unified LLM gateway.

    The gateway handles multi-provider failover (Groq → OpenAI → Gemini)
    and deterministic fallback if all providers fail.
    """
    return _llm_evaluate(
        candidate_answer=candidate_answer,
        context_summary=context_summary,
        curriculum_objectives=curriculum_objectives,
        curriculum_tools=curriculum_tools,
    )
