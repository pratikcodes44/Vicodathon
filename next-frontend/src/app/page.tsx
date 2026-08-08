"use client";

import { useState, useEffect } from "react";
import { CandidateList } from "@/components/CandidateList";
import { ChatArea } from "@/components/ChatArea";
import { ScorecardPanel } from "@/components/ScorecardPanel";

export interface Candidate {
  id: string;
  name: string;
  jobRole: string;
  status: string;
}

export interface Metrics {
  score_communication: number;
  score_technical: number;
  score_problem_solving: number;
  max_score: number;
  summary_status: string;
}

export default function Home() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<{role: "agent"|"candidate", text: string}[]>([]);
  const [metrics, setMetrics] = useState<Metrics>({
    score_communication: 0,
    score_technical: 0,
    score_problem_solving: 0,
    max_score: 0,
    summary_status: "Select a candidate to begin"
  });
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/candidates")
      .then(res => res.json())
      .then(data => setCandidates(data))
      .catch(err => console.error(err));
  }, []);

  const fetchMetrics = async (sessionId: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/metrics/${sessionId}`);
      const data = await res.json();
      setMetrics(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectCandidate = async (candidate: Candidate) => {
    setSelectedCandidate(candidate);
    const newSessionId = crypto.randomUUID();
    setActiveSessionId(newSessionId);
    setChatHistory([]);
    setMetrics({
      score_communication: 0,
      score_technical: 0,
      score_problem_solving: 0,
      max_score: 0,
      summary_status: "Starting interview..."
    });
    setIsTyping(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: newSessionId,
          candidate: {
            member: {
              id: candidate.id,
              name: candidate.name,
              jobRole: candidate.jobRole,
              yearsExperience: 4,
              education: "MS",
              memberStatus: "COMPLETED"
            },
            missions: [],
            signals: { commitDays: 31, missionsCompleted: 31, missionsFirstTry: 31 }
          }
        })
      });
      const data = await res.json();
      if (data.reply) {
        setChatHistory([{ role: "agent", text: data.reply }]);
        await fetchMetrics(newSessionId);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!activeSessionId) return;
    
    setChatHistory(prev => [...prev, { role: "candidate", text }]);
    setIsTyping(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: activeSessionId,
          message: text
        })
      });
      const data = await res.json();
      if (data.reply) {
        setChatHistory(prev => [...prev, { role: "agent", text: data.reply }]);
      }
      await fetchMetrics(activeSessionId);
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="max-w-[1920px] mx-auto min-h-screen p-8">
      <div className="grid grid-cols-12 gap-6 h-full">
        {/* Left Column: Candidate List (col-span-3) */}
        <div className="col-span-12 lg:col-span-3">
          <CandidateList 
            candidates={candidates} 
            selectedCandidateId={selectedCandidate?.id} 
            onSelect={handleSelectCandidate} 
          />
        </div>

        {/* Middle Column: Chat Feed & Input (col-span-5) */}
        <div className="col-span-12 lg:col-span-5">
          <ChatArea 
            messages={chatHistory} 
            onSend={handleSendMessage} 
            isTyping={isTyping} 
          />
        </div>

        {/* Right Column: Scorecard Panel (col-span-4) */}
        <div className="col-span-12 lg:col-span-4">
          <ScorecardPanel 
            candidate={selectedCandidate} 
            metrics={metrics} 
          />
        </div>
      </div>
    </div>
  );
}
