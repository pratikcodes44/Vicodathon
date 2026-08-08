import type { Metadata } from "next";
import { Anybody, Hanken_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { LiquidCanvas } from "@/components/LiquidCanvas";

const anybody = Anybody({
  variable: "--font-anybody",
  subsets: ["latin"],
});

const hanken = Hanken_Grotesk({
  variable: "--font-hanken",
  subsets: ["latin"],
});

const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Interview Dashboard",
  description: "Next.js Liquid Neo-Brutalism Migration",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${anybody.variable} ${hanken.variable} ${jetbrains.variable} font-hanken min-h-screen antialiased text-slate-900 bg-[#fcf8ff]`}
      >
        <LiquidCanvas />
        {children}
      </body>
    </html>
  );
}
