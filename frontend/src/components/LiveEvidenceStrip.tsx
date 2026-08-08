interface LiveEvidenceStripProps {
  questionCount: number;
  daysCovered?: number;
}

export function LiveEvidenceStrip({ questionCount, daysCovered = 1 }: LiveEvidenceStripProps) {
  return (
    <div className="sticky top-[69px] z-10 w-full bg-transparent border-b border-white/10 px-5 py-2">
      <div className="flex items-center justify-between text-[11px] font-medium text-slate-300">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full bg-red-400 rounded-full opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"></span>
            </span>
            <span className="uppercase tracking-wider">Live</span>
          </div>
          <div className="h-3 w-[1px] bg-white/20"></div>
          <span>Q {Math.min(questionCount, 8)} / 8+</span>
        </div>
        <div>
          <span>DAYS: {daysCovered} / 4+</span>
        </div>
      </div>
    </div>
  );
}
