interface LiveEvidenceStripProps {
  questionCount: number;
  daysCovered?: number;
}

export function LiveEvidenceStrip({ questionCount, daysCovered = 1 }: LiveEvidenceStripProps) {
  return (
    <div className="sticky top-[64px] z-10 w-full bg-background/80 backdrop-blur-md border-b border-border px-4 py-2">
      <div className="flex items-center justify-between text-[11px] font-medium text-slate-400">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-ai-emerald opacity-75"></span>
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-ai-emerald"></span>
            </span>
            <span className="tracking-wide">LIVE</span>
          </div>
          <div className="h-3 w-px bg-border"></div>
          <span>Question {Math.min(questionCount, 8)} / 8+</span>
        </div>
        <div>
          <span>Days Covered: {daysCovered} / 4+</span>
        </div>
      </div>
    </div>
  );
}
