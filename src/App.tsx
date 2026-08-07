import { cn } from "./lib/utils";
import { Sparkles } from "lucide-react";

function App() {
  return (
    <div className="flex min-h-screen w-full flex-col items-center bg-[#050608] overflow-x-hidden">
      {/* Strict 390px mobile-first container */}
      <main className="relative flex min-h-screen w-full max-w-[390px] flex-col border-x border-border bg-background shadow-2xl">
        <header className="glass-header sticky top-0 z-10 flex h-14 w-full items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-ai-blue/10 border border-ai-blue/20">
              <Sparkles className="h-3.5 w-3.5 text-ai-blue" />
            </div>
            <h1 className="text-sm font-medium tracking-tight text-slate-100">
              Interview Agent
            </h1>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-ai-emerald opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-ai-emerald"></span>
            </span>
            <span className="text-xs font-medium text-slate-400 tracking-tight">Active</span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
          <div className="glass-card rounded-2xl p-4 text-[14px] leading-relaxed text-slate-300">
            <p>Welcome to the interview. Could you please start by introducing yourself and sharing your background?</p>
          </div>
        </div>

        <div className="glass-header mt-auto p-4 pb-8">
          <div className="glass-card flex h-11 w-full items-center rounded-full px-4 text-sm text-slate-500 transition-colors hover:border-white/10">
            Reply to the agent...
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
