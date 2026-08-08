import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal

client = TestClient(app)

def setup_function():
    """Clear and recreate the SQLite database state before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def _get_candidate(cand_id: str):
    with open("app/data/candidates.json", "r") as f:
        candidates = json.load(f)
    for c in candidates:
        if c["member"]["id"] == cand_id:
            return c
    raise ValueError(f"Candidate {cand_id} not found")

def run_interview_lifecycle(cand_id: str):
    """Helper to run a full interview lifecycle."""
    candidate = _get_candidate(cand_id)
    session_id = f"test-session-{cand_id}"
    
    # Start request
    resp = client.post("/api/interview", json={
        "sessionId": session_id,
        "candidate": candidate
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["done"] is False
    assert "reply" in data
    
    # Run turns until completion or max iterations to avoid infinite loop
    max_turns = 20
    turn_count = 0
    
    while turn_count < max_turns:
        turn_count += 1
        resp = client.post("/api/interview", json={
            "sessionId": session_id,
            "message": f"This is an answer for turn {turn_count} from {cand_id}."
        })
        assert resp.status_code == 200, resp.text
        data = resp.json()
        
        if data["done"]:
            # Interview finished
            break
            
    # Assertions
    assert data["done"] is True, f"Interview for {cand_id} did not finish within {max_turns} turns"
    assert "feedback" in data
    
    feedback = data["feedback"]
    assert "summary" in feedback
    assert isinstance(feedback["summary"], str)
    assert "strengths" in feedback
    assert isinstance(feedback["strengths"], list)
    assert "gaps" in feedback
    assert isinstance(feedback["gaps"], list)
    assert "next" in feedback
    assert isinstance(feedback["next"], list)
    
    # Validate DB constraints via the SQLite session directly
    db = SessionLocal()
    from app.core.database import InterviewSessionModel
    db_session = db.query(InterviewSessionModel).filter_by(session_id=session_id).first()
    assert db_session is not None
    assert db_session.question_count >= 8, f"Early termination! Expected >= 8, got {db_session.question_count}"
    assert len(set(db_session.covered_days)) >= 4, f"Insufficient topics covered. Expected >= 4, got {len(set(db_session.covered_days))}"
    db.close()

def test_cand_018_lifecycle():
    """Test full lifecycle for strong candidate CAND-018."""
    run_interview_lifecycle("CAND-018")

def test_cand_010_lifecycle():
    """Test full lifecycle for mixed candidate CAND-010."""
    run_interview_lifecycle("CAND-010")
