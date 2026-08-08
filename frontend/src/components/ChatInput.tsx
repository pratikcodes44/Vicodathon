import { useState } from "react";
import { motion } from "framer-motion";


interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-white/5 backdrop-blur-3xl border-t border-white/10 mt-auto p-4 pb-6 z-20">
      <div className="relative flex w-full items-center gap-2">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Message AI Interviewer..."
          className="h-12 w-full bg-white/10 border border-white/20 rounded-full px-5 text-[15px] font-medium text-white placeholder:text-white/50 focus:outline-none focus:ring-0 focus:border-white/40 focus:bg-white/15 transition-all disabled:opacity-50 shadow-inner"
        />
        <motion.button
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          className="glass-btn flex h-12 w-12 items-center justify-center rounded-full text-white disabled:opacity-50 flex-shrink-0"
        >
          <svg className="w-5 h-5 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 12h14M12 5l7 7-7 7" /></svg>
        </motion.button>
      </div>
    </div>
  );
}
