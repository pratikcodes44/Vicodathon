import { ShieldCheck, UserCircle } from "lucide-react";

export function CandidateProfileStrip() {
  return (
    <div className="glass-header sticky top-0 z-20 flex w-full flex-col px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-ai-blue/10 border border-ai-blue/20">
            <UserCircle className="h-6 w-6 text-ai-blue" />
          </div>
          <div className="flex flex-col">
            <h2 className="text-sm font-semibold text-slate-100 tracking-tight">Diane Foster</h2>
            <span className="text-xs text-slate-400">AI Engineer</span>
          </div>
        </div>
        <div className="flex items-center gap-1.5 rounded-full bg-ai-emerald/10 border border-ai-emerald/20 px-2.5 py-1">
          <ShieldCheck className="h-3.5 w-3.5 text-ai-emerald" />
          <span className="text-[10px] font-medium text-ai-emerald uppercase tracking-wider">31/31 Missions</span>
        </div>
      </div>
    </div>
  );
}
