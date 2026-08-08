"""
Curriculum Pydantic models.

Represents the canonical 31-day curriculum and any associated metadata.
Loaded from ``curriculum.json`` or the ``curriculum_days`` DB table at startup.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CurriculumDay(BaseModel):
    """One day from the 31-day AI Builder curriculum.

    Used both as a DB row model and as the in-memory curriculum reference
    for the question generator and interview planner.
    """

    day: int = Field(..., ge=1, le=31, description="Curriculum day number (PK)")
    module_no: int = Field(..., ge=1, description="Module number (1-8)")
    module_title: str = Field(..., description="Module name, e.g. 'Embeddings & Vector Search'")
    title: str = Field(..., description="Day title, e.g. 'Embeddings Explained'")
    day_type: str = Field(
        ...,
        description="Category: AI_CORE | BUILD | SHIP_IT | CAPSTONE | etc.",
    )
    tools: list[str] = Field(
        default_factory=list,
        description="Tools/technologies covered this day",
    )
    objectives: list[str] = Field(
        default_factory=list,
        description="Learning objectives for this day",
    )


class FallbackQuestion(BaseModel):
    """A deterministic fallback question from the local question bank.

    Used when the LLM fails to generate a question after two attempts.
    Keyed by curriculum ``day`` and ``difficulty`` so the orchestrator can
    pick an appropriate recovery question for the current interview plan.
    """

    day: int = Field(..., ge=1, le=31, description="Curriculum day this question targets")
    difficulty: str = Field(
        ...,
        description="Difficulty tier: FOUNDATION | APPLIED | SYSTEMS",
    )
    question_text: str = Field(
        ..., min_length=10, description="The full question text"
    )
    rubric: dict = Field(
        default_factory=dict,
        description="Expected answer rubric for manual or LLM evaluation",
    )
