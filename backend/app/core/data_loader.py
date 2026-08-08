"""
Data loader utility.

Reads curriculum.json, candidates.json, and fallback_questions.json into
memory on application startup.  The curriculum is keyed by integer ``day``
(the canonical join key — never by title).

All data is loaded once and held in module-level singletons accessed via
``get_curriculum()``, ``get_candidates()``, and ``get_fallback_questions()``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from app.core.config import CURRICULUM_PATH, CANDIDATES_PATH, FALLBACK_QUESTIONS_PATH
from app.models.curriculum import CurriculumDay, FallbackQuestion
from app.models.candidate import CandidateProfile

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module-level singletons (populated by ``load_all()``)
# ---------------------------------------------------------------------------

# Curriculum keyed by integer day for O(1) lookup
_curriculum: dict[int, CurriculumDay] = {}

# Demo candidates keyed by member.id
_candidates: dict[str, CandidateProfile] = {}

# Fallback questions keyed by (day, difficulty) for deterministic recovery
_fallback_questions: dict[tuple[int, str], list[FallbackQuestion]] = {}


# ---------------------------------------------------------------------------
# Individual loaders
# ---------------------------------------------------------------------------

def _load_curriculum(path: Path) -> dict[int, CurriculumDay]:
    """Load curriculum.json and index by integer day."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    curriculum: dict[int, CurriculumDay] = {}
    for entry in raw:
        day_obj = CurriculumDay.model_validate(entry)
        curriculum[day_obj.day] = day_obj

    logger.info("Loaded %d curriculum days from %s", len(curriculum), path)
    return curriculum


def _load_candidates(path: Path) -> dict[str, CandidateProfile]:
    """Load candidates.json and index by candidate member.id."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    candidates: dict[str, CandidateProfile] = {}
    for entry in raw:
        profile = CandidateProfile.model_validate(entry)
        candidates[profile.member.id] = profile

    logger.info("Loaded %d demo candidates from %s", len(candidates), path)
    return candidates


def _load_fallback_questions(
    path: Path,
) -> dict[tuple[int, str], list[FallbackQuestion]]:
    """Load fallback_questions.json and index by (day, difficulty)."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    questions: dict[tuple[int, str], list[FallbackQuestion]] = {}
    for entry in raw:
        q = FallbackQuestion.model_validate(entry)
        key = (q.day, q.difficulty)
        questions.setdefault(key, []).append(q)

    total = sum(len(v) for v in questions.values())
    logger.info(
        "Loaded %d fallback questions across %d (day, difficulty) keys from %s",
        total,
        len(questions),
        path,
    )
    return questions


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_all() -> None:
    """Load all JSON data assets into memory.

    Called once during FastAPI ``lifespan`` startup.  Raises on any
    parse/validation error so the app fails fast with a clear message.
    """
    global _curriculum, _candidates, _fallback_questions

    _curriculum = _load_curriculum(CURRICULUM_PATH)
    _candidates = _load_candidates(CANDIDATES_PATH)
    _fallback_questions = _load_fallback_questions(FALLBACK_QUESTIONS_PATH)

    logger.info(
        "All data assets loaded: %d curriculum days, %d candidates, %d fallback keys",
        len(_curriculum),
        len(_candidates),
        len(_fallback_questions),
    )


def get_curriculum() -> dict[int, CurriculumDay]:
    """Return the curriculum dictionary keyed by integer day."""
    return _curriculum


def get_curriculum_day(day: int) -> Optional[CurriculumDay]:
    """Look up a single curriculum day, or None if not found."""
    return _curriculum.get(day)


def get_candidates() -> dict[str, CandidateProfile]:
    """Return demo candidates keyed by member.id."""
    return _candidates


def get_fallback_questions() -> dict[tuple[int, str], list[FallbackQuestion]]:
    """Return fallback questions keyed by (day, difficulty)."""
    return _fallback_questions


def get_fallback_for(day: int, difficulty: str) -> Optional[FallbackQuestion]:
    """Get the first available fallback question for a given day and difficulty.

    Falls back to any difficulty for that day if the exact match isn't found.
    Returns None only if there are no fallback questions for that day at all.
    """
    key = (day, difficulty)
    candidates = _fallback_questions.get(key)
    if candidates:
        return candidates[0]

    # Try any difficulty for this day
    for (d, _diff), qs in _fallback_questions.items():
        if d == day and qs:
            return qs[0]

    return None
