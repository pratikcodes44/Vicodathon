import { useState, useEffect } from "react";
import { CandidateProfileStrip } from "../components/CandidateProfileStrip";
import { LiveEvidenceStrip } from "../components/LiveEvidenceStrip";
import { ChatFeed, type Message } from "../components/ChatFeed";
import { ChatInput } from "../components/ChatInput";
import { mockApi } from "../lib/mockApi";

export function InterviewLayout() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [questionCount, setQuestionCount] = useState(0);
  const [isDone, setIsDone] = useState(false);

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
      
      if (res.message) {
        setMessages((prev) => [
          ...prev,
          { id: (Date.now() + 1).toString(), role: "agent", text: res.message! }
        ]);
        setQuestionCount((prev) => prev + 1);
      }
      
      if (res.done && res.feedback) {
        setMessages((prev) => [
          ...prev,
          { 
            id: (Date.now() + 2).toString(), 
            role: "agent", 
            text: "Interview complete. " + res.feedback!.summary 
          }
        ]);
        setIsDone(true);
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
      <main className="relative flex min-h-screen w-full max-w-[390px] flex-col border-x border-border bg-background shadow-2xl">
        <CandidateProfileStrip />
        <LiveEvidenceStrip questionCount={questionCount} />
        
        <ChatFeed messages={messages} isTyping={isTyping} />
        
        <ChatInput onSend={handleSend} disabled={isTyping || isDone} />
      </main>
    </div>
  );
}
