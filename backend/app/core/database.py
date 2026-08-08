"""
Database configuration and SQLAlchemy models.
"""

from __future__ import annotations

import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from app.core.config import DATABASE_PATH

# SQLite database setup
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InterviewSessionModel(Base):
    __tablename__ = "interview_sessions"

    session_id = Column(String, primary_key=True, index=True)
    candidate_snapshot = Column(JSON, nullable=False)
    plan = Column(JSON, nullable=False, default=list)
    plan_index = Column(Integer, default=0, nullable=False)
    turns_in_current_day = Column(Integer, default=0, nullable=False)
    total_questions = Column(Integer, default=0, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")
    
    # Cumulative metrics
    score_communication = Column(Integer, nullable=False, default=0)
    score_technical = Column(Integer, nullable=False, default=0)
    score_problem_solving = Column(Integer, nullable=False, default=0)

    # Relationship to turns
    turns = relationship("InterviewTurnModel", back_populates="session", cascade="all, delete-orphan", order_by="InterviewTurnModel.turn_no")


class InterviewTurnModel(Base):
    __tablename__ = "interview_turns"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("interview_sessions.session_id"), nullable=False, index=True)
    turn_no = Column(Integer, nullable=False)
    role = Column(String, nullable=False)  # 'INTERVIEWER' or 'CANDIDATE'
    content = Column(String, nullable=False)
    curriculum_day = Column(Integer, nullable=True)

    session = relationship("InterviewSessionModel", back_populates="turns")

def init_db():
    """Create the database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
