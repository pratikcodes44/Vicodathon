"use client";

import { cn } from "@/lib/utils";
import { HTMLMotionProps, motion } from "framer-motion";
import { forwardRef } from "react";

interface BrutalistButtonProps extends HTMLMotionProps<"button"> {
  variant?: "primary" | "lavender" | "emerald";
}

export const BrutalistButton = forwardRef<HTMLButtonElement, BrutalistButtonProps>(
  ({ className, children, variant = "primary", ...props }, ref) => {
    const bgClass = {
      primary: "bg-[#4f04ff] text-white",
      lavender: "bg-[#7668D1] text-white",
      emerald: "bg-emerald-500 text-black",
    }[variant];

    return (
      <motion.button
        ref={ref}
        whileTap={{ x: 8, y: 8, boxShadow: "0px 0px 0px 0px rgba(0,0,0,1)" }}
        className={cn(
          "brutalist-header px-6 py-3 border-[3px] border-black rounded-none shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-colors",
          bgClass,
          className
        )}
        {...props}
      >
        {children}
      </motion.button>
    );
  }
);
BrutalistButton.displayName = "BrutalistButton";
