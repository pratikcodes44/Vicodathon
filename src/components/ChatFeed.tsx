import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "../lib/utils";

export interface Message {
  id: string;
  role: "agent" | "candidate";
  text: string;
}

interface ChatFeedProps {
  messages: Message[];
  isTyping: boolean;
}

export function ChatFeed({ messages, isTyping }: ChatFeedProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-5">
      <AnimatePresence initial={false}>
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
            className={cn(
              "flex w-full",
              msg.role === "candidate" ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cn(
                "max-w-[85%] rounded-2xl px-4 py-3 text-[14px] leading-relaxed shadow-sm",
                msg.role === "agent"
                  ? "bg-gradient-to-br from-surface to-slate-900 border border-ai-blue/20 text-slate-200 rounded-tl-sm"
                  : "bg-ai-blue/10 border border-ai-blue/30 text-ai-blue rounded-tr-sm"
              )}
            >
              {msg.text}
            </div>
          </motion.div>
        ))}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex w-full justify-start"
          >
            <div className="max-w-[85%] rounded-2xl bg-surface border border-border px-4 py-4 text-[14px] text-slate-400 rounded-tl-sm flex items-center gap-1.5 shadow-sm">
              <span className="h-1.5 w-1.5 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: "0ms" }}></span>
              <span className="h-1.5 w-1.5 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: "150ms" }}></span>
              <span className="h-1.5 w-1.5 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: "300ms" }}></span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <div ref={bottomRef} className="h-2" />
    </div>
  );
}
