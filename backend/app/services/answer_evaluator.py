"""
Answer Evaluator service using OpenAI structured outputs.
"""
import os
import logging
from openai import OpenAI
from app.models.interview import AnswerEvaluation

logger = logging.getLogger(__name__)

# Note: In a real production setup, the API key should be checked carefully.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy-key"))

def evaluate_answer(
    candidate_answer: str,
    context_summary: str,
    curriculum_objectives: list[str],
    curriculum_tools: list[str]
) -> AnswerEvaluation:
    """
    Evaluates the candidate's last message using OpenAI structured outputs.
    """
    prompt = f"""
    You are an expert technical interviewer evaluating a candidate's answer.
    
    Context Summary so far: {context_summary}
    Current Topic Objectives: {curriculum_objectives}
    Current Topic Tools: {curriculum_tools}
    
    Candidate Answer: {candidate_answer}
    
    Evaluate the answer and provide structured feedback. Be objective and critically evaluate the depth and correctness.
    """
    
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a technical interviewer evaluator."},
                {"role": "user", "content": prompt}
            ],
            response_format=AnswerEvaluation,
            temperature=0.2,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        logger.error(f"Failed to evaluate answer: {e}")
        from app.models.interview import DifficultyLevel, FollowUpType
        return AnswerEvaluation(
            score=2,
            correctness="Fallback correctness due to error",
            depth="Fallback depth",
            communication="Fallback communication",
            misconceptions=[],
            evidence=[],
            follow_up_needed=False,
            follow_up_type=FollowUpType.NONE,
            follow_up_focus="",
            recommended_next_difficulty=DifficultyLevel.APPLIED
        )
