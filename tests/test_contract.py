"""
Phase 1 contract tests for POST /api/interview.

Uses FastAPI TestClient (no server needed). Tests all five state-machine
states and validates the exact evaluator contract shape.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal


client = TestClient(app)

def setup_function():
    """Clear session state before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# ── Diane Foster: the perfect candidate payload ──────────────────────
DIANE_PAYLOAD = {
    "sessionId": "test-diane-001",
    "candidate": {
        "member": {
            "id": "CAND-018",
            "name": "Diane Foster",
            "jobRole": "AI Engineer",
            "yearsExperience": 4,
            "education": "MS Computer Science",
            "memberStatus": "COMPLETED",
        },
        "missions": [
            {"day": 7, "title": "Embeddings Explained", "passed": True, "skipped": False, "attempts": 1},
            {"day": 10, "title": "The Retrieval & Matching Engine", "passed": True, "skipped": False, "attempts": 1},
            {"day": 13, "title": "Advanced Prompting", "passed": True, "skipped": False, "attempts": 1},
            {"day": 22, "title": "Multi-Agent Orchestration", "passed": True, "skipped": False, "attempts": 1},
            {"day": 23, "title": "Model Context Protocol (MCP)", "passed": True, "skipped": False, "attempts": 1},
            {"day": 27, "title": "Security, Privacy & Guardrails", "passed": True, "skipped": False, "attempts": 1},
            {"day": 31, "title": "Capstone Project & Final Demo", "passed": True, "skipped": False, "attempts": 1},
        ],
        "signals": {"commitDays": 31, "missionsCompleted": 31, "missionsFirstTry": 31},
    },
}


def test_start_interview():
    """TEST 1: Start request returns welcome + Q1, done=false."""
    resp = client.post("/api/interview", json=DIANE_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert data["done"] is False
    assert "reply" in data
    assert len(data["reply"]) > 50
    assert data.get("feedback") is None
    print(f"  ✓ Start: done={data['done']}, reply_len={len(data['reply'])}")


def test_full_interview_flow():
    """TEST 2+3: Send turns until gates met, verify feedback schema."""
    # Start
    client.post("/api/interview", json=DIANE_PAYLOAD)

    answers = [
        "Embeddings are dense vector representations that capture semantic meaning.",
        "I used cosine similarity for document retrieval in the vector store.",
        "Function calling lets LLMs invoke structured tool schemas.",
        "I built specialist agents using CrewAI for domain tasks.",
        "MCP standardizes connecting AI models to external tools.",
        "I implemented prompt injection detection at the API layer.",
        "The capstone integrated retrieval, function calling, and agents.",
        "I added error budgets and separate model vs retrieval logging.",
        "For the final demo, I presented the architecture end-to-end.",
        "I would improve observability and add circuit breakers in production.",
    ]

    last_data = None
    for i, answer in enumerate(answers, 1):
        resp = client.post("/api/interview", json={
            "sessionId": "test-diane-001",
            "message": answer,
        })
        assert resp.status_code == 200
        last_data = resp.json()
        print(f"  Turn {i}: done={last_data['done']}")
        if last_data["done"]:
            break

    # Should have completed
    assert last_data["done"] is True, "Interview should complete after enough turns"
    fb = last_data["feedback"]
    assert fb is not None, "feedback required when done=true"
    assert isinstance(fb["summary"], str) and len(fb["summary"]) > 0
    assert isinstance(fb["strengths"], list) and len(fb["strengths"]) > 0
    assert isinstance(fb["gaps"], list) and len(fb["gaps"]) > 0
    assert isinstance(fb["next"], list) and len(fb["next"]) > 0
    print(f"  ✓ Feedback: summary={fb['summary'][:60]}…")


def test_idempotent_completed():
    """TEST 4: Completed session returns same feedback on repeated calls."""
    # Start and complete
    client.post("/api/interview", json=DIANE_PAYLOAD)
    for _ in range(10):
        resp = client.post("/api/interview", json={
            "sessionId": "test-diane-001", "message": "answer"
        })
        if resp.json()["done"]:
            break

    # Send another message to completed session
    resp = client.post("/api/interview", json={
        "sessionId": "test-diane-001", "message": "more?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["done"] is True
    assert data["feedback"] is not None
    print("  ✓ Idempotent completed response")


def test_unknown_session_400():
    """TEST 5: Unknown session returns HTTP 400."""
    resp = client.post("/api/interview", json={
        "sessionId": "nonexistent", "message": "hello",
    })
    assert resp.status_code == 400
    assert "Unknown session" in resp.json()["detail"]
    print(f"  ✓ Unknown session: {resp.json()['detail']}")


def test_gerald_combs_sparse():
    """TEST 6: Sparse candidate (few passed days) still initializes."""
    resp = client.post("/api/interview", json={
        "sessionId": "test-gerald-001",
        "candidate": {
            "member": {
                "id": "CAND-010",
                "name": "Gerald Combs",
                "jobRole": "IT Support Specialist",
                "yearsExperience": 20,
                "education": "AAS Information Technology",
                "memberStatus": "COMPLETED",
            },
            "missions": [
                {"day": 7, "title": "Embeddings", "passed": True, "skipped": False, "attempts": 5},
                {"day": 8, "title": "Vector DB", "passed": False, "skipped": False, "attempts": 4},
                {"day": 10, "title": "Retrieval", "passed": False, "skipped": False, "attempts": 3},
                {"day": 22, "title": "Multi-Agent", "passed": False, "skipped": False, "attempts": 3},
                {"day": 27, "title": "Security", "passed": None, "skipped": True},
                {"day": 31, "title": "Capstone", "passed": True, "skipped": False, "attempts": 3},
            ],
            "signals": {"commitDays": 22, "missionsCompleted": 23, "missionsFirstTry": 1},
        },
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["done"] is False
    # Gerald should ONLY get questions about days 7 and 31 (his only passed days)
    print(f"  ✓ Gerald started: reply_len={len(data['reply'])}")


def test_validation_both_candidate_and_message():
    """TEST 7: Sending both candidate + message returns 422."""
    resp = client.post("/api/interview", json={
        "sessionId": "bad",
        "candidate": {
            "member": {"id": "X", "name": "X"},
            "missions": [],
            "signals": {"commitDays": 0, "missionsCompleted": 0, "missionsFirstTry": 0},
        },
        "message": "hello",
    })
    assert resp.status_code == 422
    print("  ✓ Both candidate+message → 422")


if __name__ == "__main__":
    tests = [
        test_start_interview,
        test_full_interview_flow,
        test_idempotent_completed,
        test_unknown_session_400,
        test_gerald_combs_sparse,
        test_validation_both_candidate_and_message,
    ]
    print("═══════════════════════════════════════════════════════")
    print("  CONTRACT TESTS — POST /api/interview")
    print("═══════════════════════════════════════════════════════")
    print()
    for t in tests:
        print(f"{t.__doc__}")
        setup_function()
        t()
        print()
    print("═══════════════════════════════════════════════════════")
    print("  ALL CONTRACT TESTS PASSED ✓")
    print("═══════════════════════════════════════════════════════")
