import { BrutalistCard } from "./BrutalistCard";

export function CandidateList() {
  return (
    <BrutalistCard className="h-[calc(100vh-64px)] flex flex-col gap-4 overflow-y-auto">
      <h2 className="brutalist-header text-xl border-b-[3px] border-black pb-2">Candidates</h2>
      
      <div className="flex flex-col gap-3 mt-4">
        {["Diane Foster", "Alex Thompson", "Sarah Chen", "Michael Lee"].map((name, i) => (
          <div key={i} className="border-[3px] border-black p-4 cursor-pointer hover:bg-[#4f04ff] hover:text-white transition-colors bg-white/40">
            <h3 className="brutalist-header text-sm">{name}</h3>
            <span className="brutalist-data text-xs opacity-75">{i === 0 ? "Active Interview" : "Scheduled"}</span>
          </div>
        ))}
      </div>
    </BrutalistCard>
  );
}
