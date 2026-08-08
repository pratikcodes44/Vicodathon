"""
Adaptive Follow-up Controller
"""
from app.models.interview import AnswerEvaluation, FollowUpType

def adapt_follow_up(evaluation: AnswerEvaluation) -> AnswerEvaluation:
    """
    Enforce response-driven adaptation rules in Python:
    - If score is 0 or 1: Force follow_up_type = "CLARIFY"
    - If score is 2: Keep current depth or ask for implementation details (let LLM decide)
    - If score is 3 or 4: Force follow_up_type = "SCENARIO"
    """
    if evaluation.score <= 1:
        evaluation.follow_up_type = FollowUpType.CLARIFY
        evaluation.follow_up_needed = True
    elif evaluation.score >= 3:
        evaluation.follow_up_type = FollowUpType.SCENARIO
        evaluation.follow_up_needed = True
    else:
        # Score 2: allow LLM's natural flow, but typically don't force a type
        pass
        
    return evaluation
