import { ShieldCheck } from "lucide-react";

export function CandidateProfileStrip() {
  return (
    <div className="bg-white/5 backdrop-blur-xl border-b border-white/10 sticky top-0 z-20 flex w-full flex-col px-5 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex flex-col">
            <h2 className="glass-header text-[17px] text-white">Diane Foster</h2>
            <span className="text-xs font-medium text-slate-300">AI Engineer</span>
          </div>
        </div>
        <div className="flex items-center gap-1.5 bg-emerald-500/20 border border-emerald-500/30 rounded-full px-2.5 py-1">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          <span className="text-[10px] font-semibold text-emerald-400 tracking-wide uppercase">31/31 Missions</span>
        </div>
      </div>
    </div>
  );
}
