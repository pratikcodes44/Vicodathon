"use client";

import { cn } from "@/lib/utils";
import { forwardRef } from "react";
import { motion, HTMLMotionProps } from "framer-motion";

export const BrutalistCard = forwardRef<HTMLDivElement, HTMLMotionProps<"div">>(
  ({ className, children, ...props }, ref) => {
    return (
      <motion.div
        ref={ref}
        className={cn("brutalist-card p-6", className)}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);
BrutalistCard.displayName = "BrutalistCard";
