import { motion } from "framer-motion";
import type { InterviewFeedback } from "../lib/mockApi";

interface FinalScorecardProps {
  feedback: InterviewFeedback;
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.15 }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export function FinalScorecard({ feedback }: FinalScorecardProps) {
  return (
    <motion.div 
      className="flex-1 overflow-y-auto p-5 flex flex-col gap-6 w-full text-slate-200 pb-24"
      variants={container}
      initial="hidden"
      animate="show"
      exit={{ opacity: 0, y: -20 }}
    >
      <motion.div variants={item} className="flex flex-col items-center justify-center py-4 text-center mt-4">
        <div className="h-14 w-14 bg-emerald-500/10 rounded-full flex items-center justify-center mb-4 border border-emerald-500/20 shadow-[0_0_15px_rgba(52,211,153,0.15)]">
          <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
        </div>
        <h2 className="text-xl font-semibold text-white mb-1 tracking-tight">Interview Complete</h2>
        <p className="text-sm text-slate-400">Diane Foster</p>
      </motion.div>

      <motion.div variants={item} className="bg-surface/60 backdrop-blur-md rounded-3xl p-5 border border-border shadow-lg">
        <h3 className="text-[11px] uppercase tracking-widest text-slate-500 font-semibold mb-3">Summary</h3>
        <p className="text-sm leading-relaxed text-slate-300">
          {feedback.summary}
        </p>
      </motion.div>

      <motion.div variants={item} className="flex flex-col gap-3">
        <h3 className="text-[11px] uppercase tracking-widest text-slate-500 font-semibold flex items-center gap-2">
          <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
          Key Strengths
        </h3>
        <div className="flex flex-wrap gap-2">
          {feedback.strengths.map((strength, i) => (
            <span key={i} className="px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[13px] font-medium shadow-sm">
              {strength}
            </span>
          ))}
        </div>
      </motion.div>

      <motion.div variants={item} className="flex flex-col gap-3">
        <h3 className="text-[11px] uppercase tracking-widest text-slate-500 font-semibold flex items-center gap-2">
          <svg className="w-3.5 h-3.5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          Identified Gaps
        </h3>
        <div className="flex flex-wrap gap-2">
          {feedback.gaps.map((gap, i) => (
            <span key={i} className="px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[13px] font-medium shadow-sm">
              {gap}
            </span>
          ))}
        </div>
      </motion.div>

      <motion.div variants={item} className="bg-gradient-to-b from-surface to-slate-900 rounded-3xl p-5 border border-ai-blue/20 shadow-lg mt-2 mb-4">
        <h3 className="text-[11px] uppercase tracking-widest text-ai-blue font-semibold mb-4">Recommended Next Steps</h3>
        <ul className="flex flex-col gap-3.5">
          {feedback.next.map((step, i) => (
            <li key={i} className="flex items-start gap-3 text-sm text-slate-200">
              <svg className="w-4 h-4 text-ai-blue mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              <span className="leading-relaxed">{step}</span>
            </li>
          ))}
        </ul>
      </motion.div>
    </motion.div>
  );
}
