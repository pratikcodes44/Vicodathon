export interface InterviewFeedback {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
}

/**
 * API base URL for the FastAPI backend.
 * 
 * In production (Netlify): Set NEXT_PUBLIC_API_URL env var to the Render backend URL
 * In development: Falls back to http://localhost:8000
 * 
 * IMPORTANT: NEXT_PUBLIC_* vars are inlined at BUILD TIME by Next.js.
 * They must be set in Netlify's Environment Variables BEFORE triggering a deploy.
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const sendInterviewTurn = async (_sessionId: string, payload: Record<string, unknown>) => {
  console.log("[API] Base URL:", API_BASE);
  console.log("[API] Outgoing Payload:", payload);
  
  const url = `${API_BASE}/api/interview`;
  
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unable to read error body");
      console.error(`[API] HTTP ${response.status} from ${url}:`, errorText);
      throw new Error(`HTTP error! status: ${response.status} — ${errorText}`);
    }

    const data = await response.json();
    console.log("[API] Response:", data);
    return data;
  } catch (error) {
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      console.error(`[API] Network error — cannot reach ${url}. Check CORS and backend availability.`);
    }
    console.error("[API] Error:", error);
    throw error;
  }
};
