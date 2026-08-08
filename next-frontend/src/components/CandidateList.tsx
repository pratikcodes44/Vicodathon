"use client";

import { BrutalistCard } from "./BrutalistCard";
import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

export function CandidateList({ 
  candidates, 
  activeCandidateId, 
  onSelectCandidate 
}: { 
  candidates: any[], 
  activeCandidateId: string | null,
  onSelectCandidate: (candidateId: string, sessionId: string) => void 
}) {
  const supabase = createClient();
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const handleSelect = async (candidate: any) => {
    setLoadingId(candidate.id);
    // Create a new session
    const { data: session, error } = await supabase
      .from("interview_sessions")
      .insert({ candidate_id: candidate.id, status: "in_progress" })
      .select()
      .single();

    if (session) {
      onSelectCandidate(candidate.id, session.id);
    } else {
      console.error("Failed to start session:", error);
    }
    setLoadingId(null);
  };

  return (
    <BrutalistCard className="h-[calc(100vh-64px)] flex flex-col gap-4 overflow-y-auto">
      <h2 className="brutalist-header text-xl border-b-[3px] border-black pb-2">Candidates</h2>
      
      <div className="flex flex-col gap-3 mt-4">
        {candidates.map((candidate: any) => (
          <div 
            key={candidate.id} 
            onClick={() => handleSelect(candidate)}
            className={`border-[3px] border-black p-4 cursor-pointer hover:bg-[#4f04ff] hover:text-white transition-colors ${
              activeCandidateId === candidate.id ? "bg-[#4f04ff] text-white" : "bg-white/40"
            }`}
          >
            <h3 className="brutalist-header text-sm">{candidate.name}</h3>
            <span className="brutalist-data text-xs opacity-75">
              {loadingId === candidate.id ? "Starting Session..." : `${candidate.role} - ${candidate.status}`}
            </span>
          </div>
        ))}
        {candidates.length === 0 && (
          <p className="text-sm opacity-50">No candidates found.</p>
        )}
      </div>
    </BrutalistCard>
  );
}
