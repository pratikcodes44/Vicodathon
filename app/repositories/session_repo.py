"""
In-memory session repository.

Stores ``InterviewSession`` objects by ``session_id`` for the duration of
the process.  This will be replaced with SQLite persistence in a later phase,
but the interface (get / save / exists / mark_completed) stays the same.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.models.interview import InterviewSession, SessionStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module-level session store
# ---------------------------------------------------------------------------

_sessions: dict[str, InterviewSession] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_session(session_id: str) -> Optional[InterviewSession]:
    """Retrieve a session by ID, or None if it doesn't exist."""
    return _sessions.get(session_id)


def save_session(session: InterviewSession) -> None:
    """Create or update a session in the store."""
    _sessions[session.session_id] = session
    logger.debug("Session %s saved (status=%s, q=%d, days=%d)",
                 session.session_id, session.status.value,
                 session.question_count, session.distinct_days_covered)


def session_exists(session_id: str) -> bool:
    """Check whether a session ID has been initialized."""
    return session_id in _sessions


def mark_completed(session_id: str) -> None:
    """Mark a session as COMPLETED."""
    session = _sessions.get(session_id)
    if session:
        session.status = SessionStatus.COMPLETED
        logger.info("Session %s marked COMPLETED", session_id)


def clear_all() -> None:
    """Clear all sessions (useful for testing)."""
    _sessions.clear()
    logger.info("All sessions cleared")
