import { CandidateList } from "@/components/CandidateList";
import { ChatArea } from "@/components/ChatArea";
import { ScorecardPanel } from "@/components/ScorecardPanel";

export default function Home() {
  return (
    <div className="max-w-[1920px] mx-auto min-h-screen p-8">
      <div className="grid grid-cols-12 gap-6 h-full">
        {/* Left Column: Candidate List (col-span-3) */}
        <div className="col-span-12 lg:col-span-3">
          <CandidateList />
        </div>

        {/* Middle Column: Chat Feed & Input (col-span-5) */}
        <div className="col-span-12 lg:col-span-5">
          <ChatArea />
        </div>

        {/* Right Column: Scorecard Panel (col-span-4) */}
        <div className="col-span-12 lg:col-span-4">
          <ScorecardPanel />
        </div>
      </div>
    </div>
  );
}
