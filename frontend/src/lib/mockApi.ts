export interface InterviewFeedback {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
}

export interface InterviewResponse {
  message?: string;
  done: boolean;
  feedback?: InterviewFeedback;
}

// Dummy state machine state
let currentTurn = 0;

export const mockApi = {
  async postInterview(_userMessage: string): Promise<InterviewResponse> {
    // Simulate network latency
    await new Promise(resolve => setTimeout(resolve, 800));

    currentTurn++;

    if (currentTurn === 1) {
      return {
        message: "Welcome to the interview. Could you please start by introducing yourself and sharing your background?",
        done: false,
      };
    }

    if (currentTurn > 1 && currentTurn <= 7) {
      return {
        message: `Thank you for sharing. Next question: Can you provide more detail on your experience related to turn ${currentTurn}?`,
        done: false,
      };
    }

    if (currentTurn > 7) {
      // Reset for testing again if needed, or keep it at done.
      currentTurn = 0; 
      
      return {
        done: true,
        feedback: {
          summary: "The candidate demonstrated strong foundational knowledge but struggled with deep technical explanations.",
          strengths: [
            "Good communication skills",
            "Strong understanding of core concepts",
            "Friendly and approachable demeanor"
          ],
          gaps: [
            "Lacked depth in advanced topics",
            "Could improve on structural problem solving"
          ],
          next: [
            "Proceed to technical deep-dive round",
            "Focus on systemic design questions in future"
          ]
        }
      };
    }

    return {
      message: "Unexpected state.",
      done: false,
    };
  },
  
  resetSession() {
    currentTurn = 0;
  }
};
