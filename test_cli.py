import json
import httpx

API_URL = "http://127.0.0.1:8000/api/interview"
SESSION_ID = "terminal-test-session-1"

# Load Candidate 018 (Diane Foster) from candidates.json
with open("candidates.json", "r") as f:
    data = json.load(f)
    candidate_profile = data["candidates"][17]

client = httpx.Client(timeout=120.0)

print("=" * 60)
print(f"Starting Interview: {candidate_profile['member']['name']} ({candidate_profile['member']['jobRole']})")
print("=" * 60)

# 1. Start Request
try:
    res = client.post(API_URL, json={"sessionId": SESSION_ID, "candidate": candidate_profile})
    res_data = res.json()
    print(f"\n[Interviewer]: {res_data.get('reply')}\n")
except (httpx.TimeoutException, httpx.HTTPError) as e:
    print(f"\n[Error]: Connection or timeout error during startup: {e}\n")
    res_data = {}

# 2. Conversational Loop
while not res_data.get("done", False):
    try:
        user_input = input("[You]: ")
        if not user_input.strip():
            continue
        
        try:
            res = client.post(API_URL, json={"sessionId": SESSION_ID, "message": user_input})
            res_data = res.json()
            print(f"\n[Interviewer]: {res_data.get('reply')}\n")
        except (httpx.TimeoutException, httpx.HTTPError) as e:
            print(f"\n[Error]: Connection or timeout error: {e}. Please try again.\n")
            
    except KeyboardInterrupt:
        print("\nExiting test...")
        break

# 3. Print Final Structured Feedback
if res_data.get("done"):
    print("=" * 60)
    print("FINAL FEEDBACK OBJECT")
    print("=" * 60)
    print(json.dumps(res_data.get("feedback"), indent=2))
