"""
Question Generator service — delegates to the unified LLM gateway.
"""
from app.models.interview import GeneratedQuestion, DifficultyLevel, QuestionKind
from app.services.llm_service import generate_question as _llm_generate


def generate_question(
    day: int,
    objectives: list[str],
    tools: list[str],
    difficulty: DifficultyLevel,
    question_kind: QuestionKind,
    candidate_role: str,
    context_summary: str,
    follow_up_focus: str = "",
) -> GeneratedQuestion:
    """
    Generate the next interview question via the unified LLM gateway.

    The gateway handles multi-provider failover and deterministic fallback
    from fallback_questions.json if all providers fail.
    """
    return _llm_generate(
        day=day,
        objectives=objectives,
        tools=tools,
        difficulty=difficulty,
        question_kind=question_kind,
        candidate_role=candidate_role,
        context_summary=context_summary,
        follow_up_focus=follow_up_focus,
    )
