import { useState, useEffect } from "react";
import { CandidateProfileStrip } from "../components/CandidateProfileStrip";
import { LiveEvidenceStrip } from "../components/LiveEvidenceStrip";
import { ChatFeed, type Message } from "../components/ChatFeed";
import { ChatInput } from "../components/ChatInput";
import { FinalScorecard } from "../components/FinalScorecard";
import { mockApi, type InterviewFeedback } from "../lib/mockApi";
import { AnimatePresence, motion } from "framer-motion";

export function InterviewLayout() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [questionCount, setQuestionCount] = useState(0);
  const [isDone, setIsDone] = useState(false);
  const [feedback, setFeedback] = useState<InterviewFeedback | null>(null);

  // Initialize the first message
  useEffect(() => {
    const fetchInitial = async () => {
      setIsTyping(true);
      const res = await mockApi.postInterview("start");
      if (res.message) {
        setMessages([
          { id: Date.now().toString(), role: "agent", text: res.message }
        ]);
        setQuestionCount(1);
      }
      setIsTyping(false);
    };
    fetchInitial();
  }, []);

  const handleSend = async (text: string) => {
    if (isDone) return;

    // Add candidate message
    const newMsg: Message = { id: Date.now().toString(), role: "candidate", text };
    setMessages((prev) => [...prev, newMsg]);
    setIsTyping(true);

    try {
      const res = await mockApi.postInterview(text);
      
      if (res.message && !res.done) {
        setMessages((prev) => [
          ...prev,
          { id: (Date.now() + 1).toString(), role: "agent", text: res.message! }
        ]);
        setQuestionCount((prev) => prev + 1);
      }
      
      if (res.done && res.feedback) {
        setIsDone(true);
        setFeedback(res.feedback);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex min-h-screen w-full flex-col items-center bg-[#050608] overflow-x-hidden">
      {/* Strict 390px mobile-first container */}
      <main className="relative flex min-h-screen w-full max-w-[390px] flex-col border-x border-border bg-background shadow-2xl overflow-hidden">
        <CandidateProfileStrip />
        <LiveEvidenceStrip questionCount={questionCount} />
        
        <AnimatePresence mode="wait">
          {!isDone ? (
            <motion.div 
              key="chat"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.3 }}
              className="flex-1 flex flex-col overflow-hidden w-full h-full"
            >
              <ChatFeed messages={messages} isTyping={isTyping} />
              <ChatInput onSend={handleSend} disabled={isTyping || isDone} />
            </motion.div>
          ) : (
            <motion.div
              key="scorecard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
              className="flex-1 flex flex-col overflow-hidden w-full h-full"
            >
              {feedback && <FinalScorecard feedback={feedback} />}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
