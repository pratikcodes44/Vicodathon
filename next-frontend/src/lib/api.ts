export interface InterviewFeedback {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const sendInterviewTurn = async (_sessionId: string, payload: Record<string, unknown>) => {
  console.log("[API Outgoing Payload]", payload);
  try {
    const response = await fetch(`${API_BASE}/api/interview`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("[API DEBUG] Parsed JSON from backend:", data);
    return data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};
