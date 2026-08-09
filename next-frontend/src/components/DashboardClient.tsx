"use client";

import { CandidateList } from "@/components/CandidateList";
import { ChatArea } from "@/components/ChatArea";
import { ScorecardPanel } from "@/components/ScorecardPanel";
import { useState } from "react";

export function DashboardClient({ candidates }: { candidates: any[] }) {
  const [activeCandidateId, setActiveCandidateId] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleSelectCandidate = (candidateId: string, sessionId: string) => {
    setActiveCandidateId(candidateId);
    setActiveSessionId(sessionId);
    setRefreshTrigger(0);
  };

  const handleComplete = () => {
    // Force scorecard to refresh manually
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="grid grid-cols-12 gap-6 h-full">
      {/* Left Column: Candidate List (col-span-3) */}
      <div className="col-span-12 lg:col-span-3">
        <CandidateList 
          candidates={candidates} 
          activeCandidateId={activeCandidateId}
          onSelectCandidate={handleSelectCandidate}
        />
      </div>

      {/* Middle Column: Chat Feed & Input (col-span-5) */}
      <div className="col-span-12 lg:col-span-5">
        <ChatArea 
          sessionId={activeSessionId}
          onComplete={handleComplete}
        />
      </div>

      {/* Right Column: Scorecard Panel (col-span-4) */}
      <div className="col-span-12 lg:col-span-4">
        <ScorecardPanel 
          sessionId={activeSessionId}
          refreshTrigger={refreshTrigger}
        />
      </div>
    </div>
  );
}
