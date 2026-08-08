import React from "react";
import { motion } from "framer-motion";
import type { HTMLMotionProps } from "framer-motion";
import { cn } from "./LiquidBrutalistCard";

interface BrutalistGlassButtonProps extends HTMLMotionProps<"button"> {
  children: React.ReactNode;
  variant?: "primary" | "lavender" | "emerald";
  className?: string;
}

export function BrutalistGlassButton({ children, variant = "primary", className, ...props }: BrutalistGlassButtonProps) {
  const bgClass = {
    primary: "bg-white/10 text-white hover:bg-white/20",
    lavender: "bg-white/5 text-slate-200 hover:bg-white/10",
    emerald: "bg-emerald-500/20 text-emerald-100 hover:bg-emerald-500/30",
  }[variant];

  return (
    <motion.button
      className={cn("glass-btn px-6 py-3 rounded-2xl", bgClass, className)}
      {...props}
    >
      {children}
    </motion.button>
  );
}
