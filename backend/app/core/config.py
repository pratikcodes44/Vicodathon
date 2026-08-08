"""
Application configuration.

Centralizes all settings (paths, constants, tunables) so nothing is
hard-coded in service or API layers.
"""

from __future__ import annotations

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

# Root of the app package (…/app/)
APP_DIR = Path(__file__).resolve().parent.parent

# Data directory containing JSON assets
DATA_DIR = APP_DIR / "data"

# Individual data file paths
CURRICULUM_PATH = DATA_DIR / "curriculum.json"
CANDIDATES_PATH = DATA_DIR / "candidates.json"
FALLBACK_QUESTIONS_PATH = DATA_DIR / "fallback_questions.json"

# SQLite database path (will be created on first run)
DATABASE_PATH = APP_DIR / "interview_agent.db"


# ---------------------------------------------------------------------------
# Interview hard-gate constants (enforced in Python, not the LLM)
# ---------------------------------------------------------------------------

MIN_QUESTION_COUNT = 8
MIN_DISTINCT_DAYS = 4
MIN_FOLLOW_UPS = 1
MAX_TURN_QUESTIONS = 12


# ---------------------------------------------------------------------------
# Adaptive difficulty formula weights
# ---------------------------------------------------------------------------

WEIGHT_COMPLETION = 0.40
WEIGHT_FIRST_TRY = 0.35
WEIGHT_CONSISTENCY = 0.25
TOTAL_CURRICULUM_DAYS = 31


# ---------------------------------------------------------------------------
# LLM settings — multi-provider
# ---------------------------------------------------------------------------

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # groq | openai | gemini | fallback

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Model names per provider
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Legacy alias
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

LLM_TEMPERATURE_EVAL = 0.1       # Low for evaluation/feedback
LLM_TEMPERATURE_QUESTION = 0.5   # Modest for question wording
LLM_TEMPERATURE_FEEDBACK = 0.2   # Low for feedback composition
LLM_MAX_RETRIES = 2              # Retry once, then fallback


# ---------------------------------------------------------------------------
# Context window settings
# ---------------------------------------------------------------------------

TRANSCRIPT_WINDOW = 6    # Retain last N turns verbatim for LLM context
SUMMARY_MAX_WORDS = 250  # Running summary upper bound
