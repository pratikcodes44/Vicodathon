import { BrutalistCard } from "./BrutalistCard";
import { Candidate } from "@/app/page";

interface CandidateListProps {
  candidates: Candidate[];
  selectedCandidateId?: string;
  onSelect: (c: Candidate) => void;
}

export function CandidateList({ candidates, selectedCandidateId, onSelect }: CandidateListProps) {
  return (
    <BrutalistCard className="h-[calc(100vh-64px)] flex flex-col gap-4 overflow-y-auto">
      <h2 className="brutalist-header text-xl border-b-[3px] border-black pb-2">Candidates</h2>
      
      <div className="flex flex-col gap-3 mt-4">
        {candidates.map((c, i) => {
          const isSelected = selectedCandidateId === c.id;
          return (
            <div 
              key={i} 
              onClick={() => onSelect(c)}
              className={`border-[3px] border-black p-4 cursor-pointer hover:bg-[#4f04ff] hover:text-white transition-colors ${isSelected ? "bg-[#4f04ff] text-white" : "bg-white/40"}`}
            >
              <h3 className="brutalist-header text-sm">{c.name}</h3>
              <span className="brutalist-data text-xs opacity-75">{c.status}</span>
            </div>
          );
        })}
      </div>
    </BrutalistCard>
  );
}
