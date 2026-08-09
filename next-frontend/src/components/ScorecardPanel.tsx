"use client";

import { BrutalistCard } from "./BrutalistCard";
import { useState, useEffect } from "react";
import { createClient } from "@/lib/supabase/client";

export function ScorecardPanel({ sessionId, refreshTrigger = 0 }: { sessionId: string | null, refreshTrigger?: number }) {
  const supabase = createClient();
  const [scorecard, setScorecard] = useState<any>(null);
  const [candidate, setCandidate] = useState<any>(null);

  useEffect(() => {
    if (!sessionId) {
      setScorecard(null);
      setCandidate(null);
      return;
    }

    const loadData = async () => {
      // Fetch session to get candidate
      const { data: session } = await supabase
        .from("interview_sessions")
        .select("*, candidates(*)")
        .eq("id", sessionId)
        .single();
      
      if (session) {
        setCandidate(session.candidates);
      }

      // Fetch scorecard
      const { data: score } = await supabase
        .from("scorecards")
        .select("*")
        .eq("session_id", sessionId)
        .single();
      
      if (score) {
        setScorecard(score);
      } else {
        setScorecard(null); // Not completed yet
      }
    };

    loadData();

    // We still subscribe just in case they enable Realtime in the future,
    // but we no longer strictly rely on it because of refreshTrigger.
    const channel = supabase.channel('scorecard_updates')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'scorecards', filter: `session_id=eq.${sessionId}` }, payload => {
        setScorecard(payload.new);
      })
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [sessionId, supabase, refreshTrigger]);

  if (!candidate) {
    return (
      <BrutalistCard className="h-[calc(100vh-64px)] flex flex-col gap-6 overflow-y-auto">
        <div className="flex-1 flex items-center justify-center opacity-50">
          <p className="brutalist-header text-sm">No Active Candidate</p>
        </div>
      </BrutalistCard>
    );
  }

  return (
    <BrutalistCard className="h-[calc(100vh-64px)] flex flex-col gap-6 overflow-y-auto">
      <div className="border-b-[3px] border-black pb-4 text-center">
        <h2 className="brutalist-header text-2xl text-black">{candidate.name}</h2>
        <p className="brutalist-data text-sm text-[#4f04ff] mt-1">{candidate.role}</p>
      </div>

      <div className="bg-white border-[3px] border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <h3 className="brutalist-header text-sm text-black mb-2">SUMMARY</h3>
        <p className="brutalist-data text-sm leading-relaxed">
          {scorecard ? scorecard.detailed_feedback?.summary : "Interview in progress..."}
        </p>
      </div>

      <div className="flex flex-col gap-3">
        <h3 className="brutalist-header text-sm text-black">METRICS</h3>
        <div className="flex flex-col gap-2">
          {[
            { label: "Overall", score: scorecard?.overall_score },
            { label: "Communication", score: scorecard?.communication_score },
            { label: "Technical", score: scorecard?.technical_score },
            { label: "Problem Solving", score: scorecard?.problem_solving_score }
          ].map((metric, i) => (
            <div key={i} className="flex justify-between items-center bg-emerald-500 border-[3px] border-black px-3 py-2 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
              <span className="brutalist-header text-xs text-black">{metric.label}</span>
              <span className="brutalist-data text-sm font-black text-black">
                {metric.score ? `${metric.score}/10` : "--/10"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </BrutalistCard>
  );
}
