"""
Question Generator & Deterministic Fallback.
"""
import os
import random
import logging
from openai import OpenAI
from app.models.interview import GeneratedQuestion, DifficultyLevel, QuestionKind
from app.core.data_loader import get_fallback_questions

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy-key"))

def generate_question(
    day: int,
    objectives: list[str],
    tools: list[str],
    difficulty: DifficultyLevel,
    question_kind: QuestionKind,
    candidate_role: str,
    context_summary: str,
    follow_up_focus: str = ""
) -> GeneratedQuestion:
    """
    Drafts natural interviewer questions using the target day's context.
    Wraps LLM call in a retry block (max 2 attempts).
    Falls back to pre-scripted questions if it fails.
    """
    prompt = f"""
    You are a technical interviewer interviewing a {candidate_role}.
    
    Topic Context (Day {day}):
    - Objectives: {objectives}
    - Tools: {tools}
    
    Difficulty Level: {difficulty.value}
    Question Kind: {question_kind.value}
    Follow-up Focus (if any): {follow_up_focus}
    
    Interview Summary so far: {context_summary}
    
    Generate the next question to ask the candidate. Keep it natural and concise.
    """
    
    attempts = 2
    for attempt in range(attempts):
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are a friendly, expert technical interviewer."},
                    {"role": "user", "content": prompt}
                ],
                response_format=GeneratedQuestion,
                temperature=0.7,
            )
            return response.choices[0].message.parsed
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed to generate question: {e}")
            
    # Fallback mechanism
    logger.error("LLM generation failed after 2 attempts. Using deterministic fallback.")
    fallback_pool = get_fallback_questions()
    key = f"{day}_{difficulty.value}"
    
    questions = fallback_pool.get(key, [])
    if not questions:
        # If specific day/difficulty is missing, fallback to any available for that day
        questions = [q for k, q_list in fallback_pool.items() if k.startswith(f"{day}_") for q in q_list]
        
    if not questions:
        # Ultimate fallback
        return GeneratedQuestion(
            question_text=f"Can you explain your experience with the topics from Day {day}?",
            curriculum_day=day,
            objective_focus="General Experience",
            difficulty=difficulty,
            question_kind=QuestionKind.ANCHOR
        )
        
    # Choose a random fallback question from the pool
    chosen = random.choice(questions)
    return GeneratedQuestion(
        question_text=chosen.get("question_text", "Can you explain this topic?"),
        curriculum_day=day,
        objective_focus=chosen.get("rubric", {}).get("expected_depth", "General"),
        difficulty=difficulty,
        question_kind=QuestionKind.ANCHOR
    )
