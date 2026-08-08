import json
from fastapi.testclient import TestClient
from app.main import app

def test_integration_payloads():
    client = TestClient(app)
    
    # 1. Health check
    response = client.get("/api/health")
    assert response.status_code == 200, "Health check failed"
    print("Health Check Payload:", response.json())
    
    # 2. Get a sample candidate
    with open("app/data/candidates.json", "r") as f:
        candidates = json.load(f)
    candidate = candidates[0]
    
    session_id = "test-integration-session-123"
    
    # 3. Start Request
    start_payload = {
        "sessionId": session_id,
        "candidate": candidate
    }
    print("\nSending Start Request...")
    response = client.post("/api/interview", json=start_payload)
    assert response.status_code == 200, f"Start Request Failed: {response.text}"
    start_resp_data = response.json()
    print("Start Response:", json.dumps(start_resp_data, indent=2))
    assert "reply" in start_resp_data
    assert start_resp_data.get("done") is False
    
    # 4. Turn Request
    turn_payload = {
        "sessionId": session_id,
        "message": "Hello, I am ready for the interview!"
    }
    print("\nSending Turn Request...")
    response = client.post("/api/interview", json=turn_payload)
    assert response.status_code == 200, f"Turn Request Failed: {response.text}"
    turn_resp_data = response.json()
    print("Turn Response:", json.dumps(turn_resp_data, indent=2))
    assert "reply" in turn_resp_data
    assert turn_resp_data.get("done") is False

if __name__ == "__main__":
    test_integration_payloads()
    print("\nAll integration payloads verified successfully!")
