"""
Final Feedback Composer service using OpenAI structured outputs.
"""
import os
import logging
from openai import OpenAI
from app.models.interview import GeneratedFeedback, InterviewTurn

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy-key"))

def compose_final_feedback(
    candidate_role: str,
    turns: list[InterviewTurn]
) -> GeneratedFeedback:
    """
    Synthesize the final feedback object conforming exactly to technical-spec.md.
    """
    # Compile a mini-transcript for the LLM
    transcript = "\n".join(
        f"{t.role} (Turn {t.turn_no}): {t.content}" for t in turns
    )

    prompt = f"""
    You are an expert technical interviewer. You have just completed an interview with a {candidate_role}.
    
    Interview Transcript:
    {transcript}
    
    Synthesize the final feedback. The output must strictly follow this structure:
    - summary: concise overview of overall candidate performance.
    - strengths: actionable points supported strictly by high-scoring or well-answered turns.
    - gaps: actionable points supported strictly by low-scoring turns or explicit candidate weaknesses.
    - next: actionable recommendations for future learning.
    """
    
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a senior technical interviewer providing final feedback."},
                {"role": "user", "content": prompt}
            ],
            response_format=GeneratedFeedback,
            temperature=0.3,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        logger.error(f"Failed to compose final feedback: {e}")
        # Fallback feedback
        return GeneratedFeedback(
            summary="The candidate completed the interview.",
            strengths=["Completed all questions"],
            gaps=["None noted due to evaluation error"],
            next=["Continue learning"]
        )
