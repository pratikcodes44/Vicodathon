"""
Question Generator service — delegates to the unified LLM gateway.
"""
from app.models.interview import GeneratedQuestion, DifficultyLevel, QuestionKind
from app.services.llm_service import generate_question as _llm_generate


async def generate_question(
    day: int,
    title: str,
    objectives: list[str],
    tools: list[str],
    difficulty: DifficultyLevel,
    question_kind: QuestionKind,
    candidate_role: str,
    last_question: str = "",
    last_answer: str = "",
    follow_up_focus: str = "",
) -> GeneratedQuestion:
    """
    Generate the next interview question via the unified LLM gateway.

    The gateway handles multi-provider failover and deterministic fallback
    from fallback_questions.json if all providers fail.
    """
    return await _llm_generate(
        day=day,
        title=title,
        objectives=objectives,
        tools=tools,
        difficulty=difficulty,
        question_kind=question_kind,
        candidate_role=candidate_role,
        last_question=last_question,
        last_answer=last_answer,
        follow_up_focus=follow_up_focus,
    )
