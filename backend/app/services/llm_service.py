"""
Unified LLM Gateway — multi-provider service with structured JSON outputs.

Supports Groq, OpenAI, and Google Gemini with automatic provider failover
and deterministic offline recovery via fallback_questions.json.

Environment variable ``LLM_PROVIDER`` controls the primary provider:
  groq     → Groq Cloud  (llama-3.3-70b-versatile)
  openai   → OpenAI      (gpt-4o-mini)
  gemini   → Google      (gemini-2.0-flash)
  fallback → Skip LLM entirely; use pre-scripted deterministic responses

The gateway tries the primary provider first, then falls back through
the remaining providers in order, and finally resorts to offline
deterministic responses if all API calls fail.
"""

from __future__ import annotations

import json
import logging
import random
from typing import Any, Optional

from pydantic import BaseModel

from app.core.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GEMINI_API_KEY,
    OPENAI_MODEL,
    GROQ_MODEL,
    GEMINI_MODEL,
    LLM_TEMPERATURE_EVAL,
    LLM_TEMPERATURE_QUESTION,
    LLM_TEMPERATURE_FEEDBACK,
    LLM_MAX_RETRIES,
)
from app.models.interview import (
    AnswerEvaluation,
    GeneratedQuestion,
    GeneratedFeedback,
    DifficultyLevel,
    QuestionKind,
    FollowUpType,
    InterviewTurn,
)
from app.core.data_loader import get_fallback_for

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# Provider abstraction
# ═══════════════════════════════════════════════════════════════════════════

def _provider_order() -> list[str]:
    """Return the ordered list of providers to attempt, primary first."""
    all_providers = ["nvidia", "groq", "openai", "gemini"]
    primary = LLM_PROVIDER.lower()
    if primary == "fallback":
        return []
    ordered = [primary] if primary in all_providers else []
    for p in all_providers:
        if p not in ordered:
            ordered.append(p)
    return ordered


def _get_client_and_model(provider: str, response_model: type[BaseModel] | None = None) -> tuple[Any, str]:
    """Return an OpenAI-compatible client and model name for the provider."""
    from openai import AsyncOpenAI
    import os

    if provider == "nvidia":
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY not set. Please set it to use the NVIDIA API.")
        client = AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
        )
        
        # Route models based on the required task (response_model type)
        if response_model and response_model.__name__ == "GeneratedQuestion":
            model = "meta/llama-3.1-8b-instruct"
        else:
            model = "meta/llama-3.1-70b-instruct"
        return client, model

    elif provider == "groq":
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set")
        client = AsyncOpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        return client, GROQ_MODEL

    elif provider == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        return client, OPENAI_MODEL

    elif provider == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")
        client = AsyncOpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        return client, GEMINI_MODEL

    raise ValueError(f"Unknown provider: {provider}")


# ═══════════════════════════════════════════════════════════════════════════
# Core LLM call with multi-provider failover
# ═══════════════════════════════════════════════════════════════════════════

async def _call_llm_structured(
    system_prompt: str,
    user_prompt: str,
    response_model: type[BaseModel],
    temperature: float = 0.2,
) -> Optional[BaseModel]:
    """
    Attempt a structured-output LLM call across all configured providers.

    For each provider, retries up to LLM_MAX_RETRIES times.  If all providers
    are exhausted, returns None so callers can fall back to deterministic logic.
    """
    providers = _provider_order()
    if not providers:
        logger.info("LLM_PROVIDER=fallback — skipping all LLM calls.")
        return None

    for provider in providers:
        for attempt in range(1, LLM_MAX_RETRIES + 1):
            try:
                client, model = _get_client_and_model(provider, response_model)
                logger.debug(
                    "LLM call: provider=%s model=%s attempt=%d", provider, model, attempt
                )

                # Try structured parse first (OpenAI native)
                try:
                    response = await client.beta.chat.completions.parse(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        response_format=response_model,
                        temperature=temperature,
                    )
                    result = response.choices[0].message.parsed
                    if result is not None:
                        logger.info("LLM call succeeded: provider=%s model=%s", provider, model)
                        return result
                except (AttributeError, TypeError):
                    pass

                if provider == "nvidia":
                    import time
                    print(f"\n[NVIDIA NIM] 🚀 Dispatching prompt to model: '{model}'")
                    start_time = time.time()
                    
                    schema_json = response_model.model_json_schema()
                    full_system_prompt = (
                        f"{system_prompt}\n\n"
                        f"You are a strict JSON API. Output ONLY valid JSON matching the requested schema. "
                        f"Do not include markdown headers, code block wrappers (```json), or introductory/outro text.\n"
                        f"{json.dumps(schema_json, indent=2)}"
                    )
                    
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": full_system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=temperature,
                        response_format={"type": "json_object"},
                    )
                    
                    elapsed = round(time.time() - start_time, 2)
                    print(f"[NVIDIA NIM] ✅ Response generated in {elapsed}s using {model}\n")
                    
                    raw_json = response.choices[0].message.content
                    parsed = json.loads(raw_json)
                    result = response_model.model_validate(parsed)
                    logger.info("LLM call succeeded (JSON mode): provider=%s model=%s", provider, model)
                    return result

                # Fallback: plain JSON mode + manual parse
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                raw_json = response.choices[0].message.content
                parsed = json.loads(raw_json)
                result = response_model.model_validate(parsed)
                logger.info("LLM call succeeded (JSON mode): provider=%s model=%s", provider, model)
                return result

            except Exception as e:
                logger.warning(
                    "LLM call failed: provider=%s attempt=%d error=%s",
                    provider, attempt, str(e)[:200],
                )

    logger.error("All LLM providers exhausted. Returning None for deterministic fallback.")
    return None


# ═══════════════════════════════════════════════════════════════════════════
# Public API: evaluate_answer
# ═══════════════════════════════════════════════════════════════════════════

async def evaluate_answer(
    candidate_answer: str,
    context_summary: str,
    curriculum_objectives: list[str],
    curriculum_tools: list[str],
) -> AnswerEvaluation:
    """
    Evaluate a candidate's answer using the 0-4 rubric.

    Returns a deterministic fallback AnswerEvaluation if all LLM calls fail.
    """
    system_prompt = (
        "You are an expert technical interviewer evaluator. "
        "Score the candidate's answer on a 0-4 rubric and provide structured feedback. "
        "You MUST respond with a JSON object matching the required schema."
    )
    user_prompt = f"""
Evaluate this candidate answer:

Context Summary: {context_summary or 'Interview in progress.'}
Topic Objectives: {curriculum_objectives}
Topic Tools: {curriculum_tools}
Candidate Answer: {candidate_answer}

Provide your evaluation as JSON with these fields:
- score (int 0-4): 0=no answer, 1=wrong, 2=partial, 3=good, 4=excellent
- correctness (str): assessment of factual correctness
- depth (str): assessment of technical depth
- communication (str): assessment of clarity
- misconceptions (list[str]): any misconceptions detected
- evidence (list[str]): key claims from the answer
- follow_up_needed (bool): whether a follow-up is warranted
- follow_up_type (str): one of CLARIFY, DEEPEN, SCENARIO, NONE
- follow_up_focus (str): specific topic for follow-up
- recommended_next_difficulty (str): one of FOUNDATION, APPLIED, SYSTEMS
"""
    result = await _call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=AnswerEvaluation,
        temperature=LLM_TEMPERATURE_EVAL,
    )
    if result is not None:
        return result

    # Deterministic fallback
    logger.info("Using deterministic fallback for answer evaluation.")
    return AnswerEvaluation(
        score=2,
        correctness="Unable to evaluate via LLM — using neutral fallback.",
        depth="Moderate depth assumed.",
        communication="Communication appears adequate.",
        misconceptions=[],
        evidence=[],
        follow_up_needed=False,
        follow_up_type=FollowUpType.NONE,
        follow_up_focus="",
        recommended_next_difficulty=DifficultyLevel.APPLIED,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Public API: generate_question
# ═══════════════════════════════════════════════════════════════════════════

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
    Generate the next interview question via LLM, with deterministic fallback.
    """
    system_prompt = (
        "You are a friendly, expert technical interviewer. "
        "Generate natural, concise interview questions. "
        "You MUST respond with a JSON object matching the required schema."
    )
    # Context Isolation: Include ONLY the immediate last question and answer if it's a follow-up
    recent_context = ""
    if question_kind != QuestionKind.ANCHOR and last_question and last_answer:
        recent_context = f"Previous Question: {last_question}\nCandidate Answer: {last_answer}\n"

    user_prompt = f"""
Generate an interview question for a {candidate_role}.

You MUST ask a question about {title} (Day {day}). Do NOT ask about previous topics.

Topic Context (Day {day}):
- Title: {title}
- Objectives: {objectives}
- Tools: {tools}

Difficulty Level: {difficulty.value}
Question Kind: {question_kind.value}
Follow-up Focus: {follow_up_focus or 'None'}

{recent_context}
Respond as JSON with:
- question_text (str, min 10 chars): the question to ask
- curriculum_day (int): {day}
- objective_focus (str): which objective this targets
- difficulty (str): {difficulty.value}
- question_kind (str): {question_kind.value}
"""
    result = await _call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=GeneratedQuestion,
        temperature=LLM_TEMPERATURE_QUESTION,
    )
    if result is not None:
        return result

    # Deterministic fallback from pre-scripted bank
    logger.info("Using deterministic fallback for question generation (day=%d).", day)
    fallback_q = get_fallback_for(day, difficulty.value)
    if fallback_q:
        return GeneratedQuestion(
            question_text=fallback_q.question_text,
            curriculum_day=day,
            objective_focus=fallback_q.rubric.get("expected_depth", "General") if isinstance(fallback_q.rubric, dict) else "General",
            difficulty=difficulty,
            question_kind=question_kind,
        )

    # Ultimate fallback
    return GeneratedQuestion(
        question_text=f"Can you walk me through your experience with the topics from Day {day}?",
        curriculum_day=day,
        objective_focus="General experience",
        difficulty=difficulty,
        question_kind=QuestionKind.ANCHOR,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Public API: compose_final_feedback
# ═══════════════════════════════════════════════════════════════════════════

async def compose_final_feedback(
    candidate_role: str,
    turns: list[InterviewTurn],
) -> GeneratedFeedback:
    """
    Synthesize the final feedback from the interview transcript.
    """
    transcript_lines = [
        f"{t.role} (Turn {t.turn_no}): {t.content}" for t in turns
    ]
    transcript = "\n".join(transcript_lines)

    system_prompt = (
        "You are a senior technical interviewer providing final interview feedback. "
        "Analyze the full transcript and produce evidence-backed feedback. "
        "You MUST respond with a JSON object matching the required schema."
    )
    user_prompt = f"""
You have just completed an interview with a {candidate_role}.

Interview Transcript:
{transcript}

Synthesize final feedback as JSON with:
- summary (str): concise overview of candidate performance
- strengths (list[str]): evidence-backed strengths from high-scoring answers
- gaps (list[str]): knowledge gaps from weak answers
- next (list[str]): actionable recommendations for future learning
"""
    result = await _call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=GeneratedFeedback,
        temperature=LLM_TEMPERATURE_FEEDBACK,
    )
    if result is not None:
        return result

    # Deterministic fallback
    logger.info("Using deterministic fallback for feedback composition.")
    return GeneratedFeedback(
        summary=f"The {candidate_role} completed the interview covering multiple curriculum topics.",
        strengths=["Engaged with all interview questions", "Showed willingness to discuss technical topics"],
        gaps=["Some answers lacked implementation-level depth"],
        next=["Review advanced topics in depth", "Practice building end-to-end projects"],
    )
