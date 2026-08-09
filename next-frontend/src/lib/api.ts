export interface InterviewFeedback {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
}

// We use an empty string so fetch() uses relative paths (e.g. /api/interview)
// Next.js rewrites (next.config.ts) will proxy this to the actual backend URL.
// This completely avoids CORS issues.
const API_BASE = "";

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
