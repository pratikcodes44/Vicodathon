
import { motion } from "framer-motion";
import type { HTMLMotionProps } from "framer-motion";
import clsx from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

export function LiquidBrutalistCard({ className, children, ...props }: HTMLMotionProps<"div">) {
  return (
    <motion.div 
      className={cn("glass-panel rounded-3xl", className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}
