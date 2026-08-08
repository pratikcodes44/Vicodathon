"""
Candidate Pydantic models.

Tolerant schema that accepts the evaluator's candidate payload exactly as sent.
Fields like `attempts` and `passed` are Optional because skipped mission records
may omit them. We never infer omitted days — missing means unknown, not failed.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Mission evidence (one row per explicit curriculum-day record)
# ---------------------------------------------------------------------------

class MissionEvidence(BaseModel):
    """A single mission record from the candidate's learning journey.

    Only *explicitly present* records exist; a day absent from this list is
    unknown, NOT failed.  ``passed`` is nullable — ``None`` means no
    pass/fail verdict was recorded (e.g. the mission was skipped).
    ``attempts`` is also nullable for the same reason.
    """

    day: int = Field(..., description="Curriculum day number (1-31)")
    title: str = Field(..., description="Mission title as supplied by evaluator")
    passed: Optional[bool] = Field(
        default=None,
        description="True = passed, False = failed, None = no verdict recorded",
    )
    skipped: bool = Field(
        default=False,
        description="Whether this mission was explicitly skipped",
    )
    attempts: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of attempts; may be absent for skipped missions",
    )


# ---------------------------------------------------------------------------
# Aggregate engagement signals
# ---------------------------------------------------------------------------

class CandidateSignals(BaseModel):
    """High-level engagement metrics supplied with every candidate."""

    commitDays: int = Field(..., ge=0, description="Days the candidate committed")
    missionsCompleted: int = Field(..., ge=0, description="Total missions completed")
    missionsFirstTry: int = Field(..., ge=0, description="Missions passed on first attempt")


# ---------------------------------------------------------------------------
# Member identity (nested inside the candidate object)
# ---------------------------------------------------------------------------

class Member(BaseModel):
    """Candidate identity and professional profile.

    Uses ``model_config`` with ``extra = "allow"`` so unexpected fields from the
    evaluator payload don't crash the parser.
    """

    model_config = {"extra": "allow"}

    id: str = Field(..., description="Unique candidate identifier (e.g. CAND-018)")
    name: str = Field(..., description="Candidate's full name")
    jobRole: Optional[str] = Field(
        default=None,
        alias="jobRole",
        description="Current or target job role",
    )
    yearsExperience: Optional[int] = Field(
        default=None,
        alias="yearsExperience",
        ge=0,
        description="Years of professional experience",
    )
    education: Optional[str] = Field(
        default=None,
        description="Highest education qualification",
    )
    memberStatus: Optional[str] = Field(
        default=None,
        alias="memberStatus",
        description="E.g. COMPLETED, IN_PROGRESS",
    )


# ---------------------------------------------------------------------------
# Top-level candidate profile (the object in the first API request)
# ---------------------------------------------------------------------------

class CandidateProfile(BaseModel):
    """Complete candidate payload sent by the evaluator on the first request.

    Accepts the ``member`` block, a list of explicit ``missions``, and the
    aggregate ``signals``.  Extra top-level keys are tolerated via
    ``extra = "allow"`` so evaluator format drift won't crash the system.
    """

    model_config = {"extra": "allow", "populate_by_name": True}

    member: Member = Field(..., description="Candidate identity and role info")
    missions: list[MissionEvidence] = Field(
        default_factory=list,
        description="Explicit mission records; absent days are unknown",
    )
    signals: CandidateSignals = Field(
        ..., description="Aggregate engagement metrics"
    )

    # ----- derived helpers (not serialized) --------------------------------

    @property
    def passed_days(self) -> list[int]:
        """Sorted list of curriculum days the candidate *explicitly* passed."""
        return sorted(
            m.day for m in self.missions if m.passed is True and not m.skipped
        )

    @property
    def failed_days(self) -> list[int]:
        """Days the candidate explicitly failed (passed == False)."""
        return sorted(
            m.day for m in self.missions if m.passed is False
        )

    @property
    def skipped_days(self) -> list[int]:
        """Days the candidate explicitly skipped."""
        return sorted(m.day for m in self.missions if m.skipped)
