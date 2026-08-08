import { BrutalistCard } from "./BrutalistCard";

export function ScorecardPanel() {
  return (
    <BrutalistCard className="h-[calc(100vh-64px)] flex flex-col gap-6 overflow-y-auto">
      <div className="border-b-[3px] border-black pb-4 text-center">
        <h2 className="brutalist-header text-2xl text-black">Diane Foster</h2>
        <p className="brutalist-data text-sm text-[#4f04ff] mt-1">AI ENGINEER</p>
      </div>

      <div className="bg-white border-[3px] border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <h3 className="brutalist-header text-sm text-black mb-2">SUMMARY</h3>
        <p className="brutalist-data text-sm leading-relaxed">
          Interview in progress...
        </p>
      </div>

      <div className="flex flex-col gap-3">
        <h3 className="brutalist-header text-sm text-black">METRICS</h3>
        <div className="flex flex-col gap-2">
          {["Communication", "Technical", "Problem Solving"].map((metric, i) => (
            <div key={i} className="flex justify-between items-center bg-emerald-500 border-[3px] border-black px-3 py-2 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
              <span className="brutalist-header text-xs text-black">{metric}</span>
              <span className="brutalist-data text-sm font-black text-black">--/5</span>
            </div>
          ))}
        </div>
      </div>
    </BrutalistCard>
  );
}
