"use client";

import { motion } from "framer-motion";

export function LiquidCanvas() {
  return (
    <div className="fixed inset-0 pointer-events-none -z-10 bg-[#fcf8ff]">
      {/* Muted Lavender Blob */}
      <motion.div
        animate={{
          x: [0, 150, -100, 0],
          y: [0, -100, 150, 0],
          scale: [1, 1.2, 0.8, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#7668D1]/20 rounded-full blur-[100px]"
      />
      {/* Electric Indigo Blob */}
      <motion.div
        animate={{
          x: [0, -150, 100, 0],
          y: [0, 150, -100, 0],
          scale: [1, 0.9, 1.1, 1],
        }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-[#4f04ff]/15 rounded-full blur-[120px]"
      />
    </div>
  );
}
