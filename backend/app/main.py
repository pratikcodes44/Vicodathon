"""
FastAPI application entry point for The Interview Agent.

Initializes the app, loads data assets on startup, and mounts
the single ``POST /api/interview`` endpoint.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.interview import router as interview_router
from app.core.data_loader import load_all
from app.core.database import init_db


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("interview_agent")


# ---------------------------------------------------------------------------
# Lifespan: load data on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.

    Runs ``load_all()`` once at startup to read curriculum.json,
    candidates.json and fallback_questions.json into memory.
    """
    logger.info("Starting The Interview Agent — initializing database…")
    init_db()
    logger.info("Starting The Interview Agent — loading data assets…")
    load_all()
    logger.info("Data assets loaded — server ready")
    yield
    logger.info("Shutting down The Interview Agent")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="The Interview Agent",
    description=(
        "A stateful AI interviewer that adapts questions based on a candidate's "
        "learning journey, evaluates answers with a structured rubric, and "
        "produces evidence-backed feedback."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware configuration
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "interview-agent-backend"}

# Mount the interview router (contains POST /api/interview)
app.include_router(interview_router)
