"use client";

import { BrutalistCard } from "./BrutalistCard";
import { BrutalistButton } from "./BrutalistButton";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { createClient } from "@/lib/supabase/client";
import { sendInterviewTurn } from "@/lib/api";

export function ChatArea({ sessionId, onComplete }: { sessionId: string | null, onComplete: () => void }) {
  const supabase = createClient();
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      return;
    }
    
    // Load chat history
    const loadMessages = async () => {
      const { data } = await supabase
        .from("chat_messages")
        .select("*")
        .eq("session_id", sessionId)
        .order("created_at", { ascending: true });
      
      if (data && data.length > 0) {
        setMessages(data);
      } else {
        // Initial agent message
        const initialMsg = {
          session_id: sessionId,
          sender: "interviewer",
          content: "Welcome! We are going to assess your skills today. Ready to begin?"
        };
        await supabase.from("chat_messages").insert(initialMsg);
        setMessages([initialMsg]);
      }
    };
    loadMessages();
  }, [sessionId]);

  const handleSend = async () => {
    if (!input.trim() || !sessionId || loading) return;
    
    const userText = input;
    setInput("");
    setLoading(true);

    const userMsg = { session_id: sessionId, sender: "candidate", content: userText };
    setMessages(prev => [...prev, userMsg]);
    await supabase.from("chat_messages").insert(userMsg);

    try {
      const apiResponse = await sendInterviewTurn(sessionId, { 
        sessionId: sessionId,
        message: userText
      });

      if (apiResponse.done) {
        // Backend handles scorecard creation, we just trigger complete
        onComplete();
      } else {
        const agentMsg = { session_id: sessionId, sender: "interviewer", content: apiResponse.reply || "Error: no reply" };
        setMessages(prev => [...prev, agentMsg]);
        await supabase.from("chat_messages").insert(agentMsg);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { session_id: sessionId, sender: "system", content: "Error communicating with backend." }]);
    }
    setLoading(false);
  };

  if (!sessionId) {
    return (
      <BrutalistCard className="h-[calc(100vh-64px)] flex flex-col p-6 items-center justify-center">
        <h2 className="brutalist-header text-xl opacity-50">Select a candidate to begin</h2>
      </BrutalistCard>
    );
  }

  return (
    <BrutalistCard className="h-[calc(100vh-64px)] flex flex-col p-0 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
        {messages.map((m, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`max-w-[80%] border-[3px] border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] ${
              m.sender === "interviewer" || m.sender === "system" ? "bg-[#4f04ff] text-white self-start" : "bg-[#7668D1] text-white self-end"
            }`}
          >
            <p className="font-bold text-sm leading-relaxed">{m.content}</p>
          </motion.div>
        ))}
        {loading && <p className="text-xs opacity-50 ml-2">Thinking...</p>}
      </div>

      <div className="border-t-[3px] border-black p-4 bg-white/40 backdrop-blur-xl flex gap-2">
        <input 
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSend()}
          placeholder="TYPE MESSAGE..."
          disabled={loading}
          className="flex-1 border-[3px] border-black px-4 font-bold focus:outline-none focus:ring-0 shadow-inner bg-white h-12 disabled:opacity-50"
        />
        <BrutalistButton onClick={handleSend} disabled={loading} className="h-12 flex items-center justify-center">
          SEND
        </BrutalistButton>
      </div>
    </BrutalistCard>
  );
}
