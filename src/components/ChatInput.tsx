import { useState } from "react";
import { motion } from "framer-motion";
import { SendHorizontal } from "lucide-react";

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
    <div className="glass-header mt-auto p-4 pb-6 z-20">
      <div className="relative flex w-full items-center">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Reply to the agent..."
          className="h-12 w-full rounded-full bg-surface/80 border border-border px-4 pr-12 text-sm text-slate-200 placeholder:text-slate-500 focus:border-ai-blue/50 focus:outline-none focus:ring-1 focus:ring-ai-blue/50 transition-all disabled:opacity-50"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          className="absolute right-1.5 flex h-9 w-9 items-center justify-center rounded-full bg-ai-blue text-white disabled:opacity-50 disabled:bg-surface disabled:text-slate-500 transition-colors"
        >
          <SendHorizontal className="h-4 w-4" />
        </motion.button>
      </div>
    </div>
  );
}
