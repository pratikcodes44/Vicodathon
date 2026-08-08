"""
Feedback Pydantic model.

Exact schema required by the evaluator contract.  The final ``POST /api/interview``
response must include ``done: true`` and a ``feedback`` object validated against
this model.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class InterviewFeedback(BaseModel):
    """Structured feedback returned when the interview is complete.

    Every field is mandatory — the evaluator checks for their presence.
    ``strengths``, ``gaps``, and ``next`` are string arrays with concrete,
    evidence-backed items drawn from the scored interview turns.
    """

    summary: str = Field(
        ...,
        min_length=1,
        description="Narrative summary of the candidate's interview performance",
    )
    strengths: list[str] = Field(
        ...,
        min_length=1,
        description="Demonstrated strengths, each backed by interview evidence",
    )
    gaps: list[str] = Field(
        ...,
        min_length=1,
        description="Identified knowledge gaps or areas needing improvement",
    )
    next: list[str] = Field(
        ...,
        min_length=1,
        description="Recommended next steps for the candidate's learning path",
    )
