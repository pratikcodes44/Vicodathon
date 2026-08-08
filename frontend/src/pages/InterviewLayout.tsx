import { useState, useEffect, useRef } from "react";
import { CandidateProfileStrip } from "../components/CandidateProfileStrip";
import { LiveEvidenceStrip } from "../components/LiveEvidenceStrip";
import { ChatFeed, type Message } from "../components/ChatFeed";
import { ChatInput } from "../components/ChatInput";
import { FinalScorecard } from "../components/FinalScorecard";
import { sendInterviewTurn, type InterviewFeedback } from "../lib/api";
import { AnimatePresence, motion } from "framer-motion";

export function InterviewLayout() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [questionCount, setQuestionCount] = useState(0);
  const [isDone, setIsDone] = useState(false);
  const [feedback, setFeedback] = useState<InterviewFeedback | null>(null);
  const sessionIdRef = useRef(crypto.randomUUID());

  // Initialize the first message
  useEffect(() => {
    let ignore = false;
    const fetchInitial = async () => {
      setIsTyping(true);
      const res = await sendInterviewTurn(sessionIdRef.current, { 
        sessionId: sessionIdRef.current, 
        is_start: true,
        candidate: {
          member: {
            id: "CAND-018",
            name: "Diane Foster",
            jobRole: "AI Engineer",
            yearsExperience: 4,
            education: "MS",
            memberStatus: "COMPLETED"
          },
          missions: [],
          signals: { commitDays: 31, missionsCompleted: 31, missionsFirstTry: 31 }
        }
      });
      if (!ignore && res.reply) {
        setMessages([
          { id: Date.now().toString(), role: "agent", text: res.reply }
        ]);
        setQuestionCount(1);
      }
      if (!ignore) setIsTyping(false);
    };
    fetchInitial();
    return () => { ignore = true; };
  }, []);

  const handleSend = async (text: string) => {
    if (isDone) return;

    // Add candidate message
    const newMsg: Message = { id: Date.now().toString(), role: "candidate", text };
    setMessages((prev) => [...prev, newMsg]);
    setIsTyping(true);

    try {
      const res = await sendInterviewTurn(sessionIdRef.current, { 
        sessionId: sessionIdRef.current, 
        message: text 
      });
      
      if (res.reply && !res.done) {
        setMessages((prev) => [
          ...prev,
          { id: (Date.now() + 1).toString(), role: "agent", text: res.reply }
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
    <div className="flex min-h-screen w-full flex-col items-center justify-center overflow-x-hidden">
      {/* Strict 390px mobile-first container with Apple Liquid Glass */}
      <main className="relative flex h-[844px] w-full max-w-[390px] flex-col glass-panel rounded-[40px] overflow-hidden my-auto">
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
