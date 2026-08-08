"use client";

import { BrutalistCard } from "./BrutalistCard";
import { BrutalistButton } from "./BrutalistButton";
import { useState } from "react";
import { motion } from "framer-motion";

interface ChatAreaProps {
  messages: { role: "agent" | "candidate"; text: string }[];
  onSend: (text: string) => void;
  isTyping?: boolean;
}

export function ChatArea({ messages, onSend, isTyping = false }: ChatAreaProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim() || isTyping) return;
    onSend(input);
    setInput("");
  };

  return (
    <BrutalistCard className="h-[calc(100vh-64px)] flex flex-col p-0 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
        {messages.map((m, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`max-w-[80%] border-[3px] border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] ${
              m.role === "agent" ? "bg-[#4f04ff] text-white self-start" : "bg-[#7668D1] text-white self-end"
            }`}
          >
            <p className="font-bold text-sm leading-relaxed">{m.text}</p>
          </motion.div>
        ))}
      </div>

      <div className="border-t-[3px] border-black p-4 bg-white/40 backdrop-blur-xl flex gap-2">
        <input 
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="TYPE MESSAGE..."
          disabled={isTyping}
          className="flex-1 border-[3px] border-black px-4 font-bold focus:outline-none focus:ring-0 shadow-inner bg-white h-12 disabled:opacity-50"
        />
        <BrutalistButton onClick={handleSend} disabled={isTyping} className="h-12 flex items-center justify-center disabled:opacity-50">
          SEND
        </BrutalistButton>
      </div>
    </BrutalistCard>
  );
}
