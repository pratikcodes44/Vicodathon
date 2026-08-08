import json
import uuid
import httpx
import time

def main():
    # 1. Read candidates.json and select CAND-018
    print("Loading candidate data...")
    try:
        with open("app/data/candidates.json", "r") as f:
            candidates = json.load(f)
    except FileNotFoundError:
        print("Error: Could not find app/data/candidates.json. Make sure you are running this from the backend directory.")
        return

    candidate = next((c for c in candidates if c["member"]["id"] == "CAND-018"), None)
    if not candidate:
        print("Error: Candidate CAND-018 not found in candidates.json.")
        return

    print(f"Selected Candidate: {candidate['member']['name']} ({candidate['member']['id']})")
    
    # 2. Setup the session
    session_id = str(uuid.uuid4())
    api_url = "http://localhost:8000/api/interview"
    
    # 3. Send the initialization request
    start_payload = {
        "sessionId": session_id,
        "candidate": candidate
    }
    
    print(f"\nInitializing interview session {session_id}...\n")
    
    try:
        response = httpx.post(api_url, json=start_payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Failed to connect to the FastAPI server: {e}")
        print("Make sure the server is running on http://localhost:8000")
        return
        
    print(f"[Interviewer]: {data.get('reply')}")
    
    if data.get("done"):
        print("\nInterview completed unexpectedly during initialization.")
        return

    # 4. Create the interactive loop
    while True:
        try:
            user_input = input("\n[You]: ").strip()
            if not user_input:
                continue
                
            # Allow graceful exit
            if user_input.lower() in ['exit', 'quit', 'stop']:
                print("Exiting test script.")
                break
                
            # Send the turn request
            turn_payload = {
                "sessionId": session_id,
                "message": user_input
            }
            
            response = httpx.post(api_url, json=turn_payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            
            print(f"\n[Interviewer]: {data.get('reply')}")
            
            # Break the loop if done: true
            if data.get("done"):
                print("\n" + "="*50)
                print("INTERVIEW COMPLETED. FINAL FEEDBACK:")
                print("="*50)
                feedback = data.get("feedback")
                if feedback:
                    print(json.dumps(feedback, indent=2))
                else:
                    print("Error: done was true but no feedback object was returned.")
                break
                
        except KeyboardInterrupt:
            print("\nExiting test script.")
            break
        except httpx.HTTPStatusError as e:
            print(f"\n[API Error]: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"\n[Error]: {e}")

if __name__ == "__main__":
    # Wait a tiny bit just in case the server just started
    time.sleep(0.5)
    main()
