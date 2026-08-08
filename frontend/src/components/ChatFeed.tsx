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
                "max-w-[85%] rounded-[20px] p-4 text-[14px] font-medium leading-relaxed shadow-lg backdrop-blur-xl",
                msg.role === "agent"
                  ? "bg-white/10 border border-white/20 text-white rounded-tl-sm"
                  : "bg-white/20 border border-white/30 text-white rounded-tr-sm"
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
            <div className="max-w-[85%] border-[3px] border-black bg-slate-200 p-4 text-[14px] flex items-center gap-2 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
              <span className="h-2 w-2 bg-black animate-bounce" style={{ animationDelay: "0ms" }}></span>
              <span className="h-2 w-2 bg-black animate-bounce" style={{ animationDelay: "150ms" }}></span>
              <span className="h-2 w-2 bg-black animate-bounce" style={{ animationDelay: "300ms" }}></span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <div ref={bottomRef} className="h-2" />
    </div>
  );
}
