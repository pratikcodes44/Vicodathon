import { motion } from "framer-motion";
import type { InterviewFeedback } from "../lib/api";
import { LiquidBrutalistCard } from "./LiquidBrutalistCard";
import { BrutalistGlassButton } from "./BrutalistGlassButton";

interface FinalScorecardProps {
  feedback: InterviewFeedback;
}

const container: any = {
  hidden: { opacity: 0, scale: 0.95 },
  show: {
    opacity: 1, scale: 1,
    transition: { staggerChildren: 0.15, type: "spring", stiffness: 300, damping: 25 }
  }
};

const item: any = {
  hidden: { opacity: 0, x: -20 },
  show: { opacity: 1, x: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export function FinalScorecard({ feedback }: FinalScorecardProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4 flex flex-col items-center justify-center w-full">
      <motion.div 
        className="w-full flex flex-col gap-6"
        variants={container}
        initial="hidden"
        animate="show"
      >
        <LiquidBrutalistCard className="flex flex-col gap-6 p-6">
          <motion.div variants={item} className="flex flex-col items-center justify-center border-b border-white/10 pb-5 text-center">
            <h2 className="glass-header text-2xl text-white mb-1 tracking-tight">Interview Complete</h2>
            <p className="text-[13px] font-medium text-slate-400">Diane Foster</p>
          </motion.div>

          <motion.div variants={item} className="bg-white/5 rounded-2xl border border-white/10 p-5">
            <h3 className="glass-header text-[11px] uppercase tracking-wider text-slate-400 mb-2">SUMMARY</h3>
            <p className="text-sm leading-relaxed text-slate-200">
              {feedback.summary || "Completed the assessment."}
            </p>
          </motion.div>

          <motion.div variants={item} className="flex flex-col gap-3">
            <h3 className="glass-header text-[11px] uppercase tracking-wider text-slate-400">KEY STRENGTHS</h3>
            <div className="flex flex-wrap gap-2">
              {(feedback.strengths.length > 0 ? feedback.strengths : ["Strong Fundamentals"]).map((strength, i) => (
                <span key={i} className="px-3 py-1.5 bg-emerald-500/15 border border-emerald-500/20 text-emerald-300 rounded-full text-xs font-medium">
                  {strength}
                </span>
              ))}
            </div>
          </motion.div>

          <motion.div variants={item} className="flex flex-col gap-3">
            <h3 className="glass-header text-[11px] uppercase tracking-wider text-slate-400">IDENTIFIED GAPS</h3>
            <div className="flex flex-wrap gap-2">
              {(feedback.gaps.length > 0 ? feedback.gaps : ["None detected"]).map((gap, i) => (
                <span key={i} className="px-3 py-1.5 bg-red-500/15 border border-red-500/20 text-red-300 rounded-full text-xs font-medium">
                  {gap}
                </span>
              ))}
            </div>
          </motion.div>

          <motion.div variants={item} className="bg-white/5 rounded-2xl border border-white/10 p-5 mt-2">
            <h3 className="glass-header text-[11px] uppercase tracking-wider text-slate-400 mb-3">RECOMMENDED NEXT STEPS</h3>
            <ol className="flex flex-col gap-3 list-decimal list-inside font-medium text-slate-200 text-sm">
              {(feedback.next.length > 0 ? feedback.next : ["Proceed to next round"]).map((step, i) => (
                <li key={i} className="leading-relaxed">
                  {step}
                </li>
              ))}
            </ol>
          </motion.div>
          
          <motion.div variants={item} className="mt-4 flex justify-center">
            <BrutalistGlassButton className="w-full text-lg" onClick={() => window.location.reload()}>
              FINISH
            </BrutalistGlassButton>
          </motion.div>
        </LiquidBrutalistCard>
      </motion.div>
    </div>
  );
}
