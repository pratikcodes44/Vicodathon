import { InterviewLayout } from "./pages/InterviewLayout";
import { motion } from "framer-motion";

function App() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0f1015] text-slate-100 font-sans">
      {/* Premium Apple Liquid Glass Canvas */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <motion.div
          animate={{
            x: [0, 80, -80, 0],
            y: [0, -80, 80, 0],
            scale: [1, 1.1, 0.9, 1],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 left-1/4 w-[40rem] h-[40rem] bg-[#5ac8fa]/15 rounded-full blur-[100px]"
        />
        <motion.div
          animate={{
            x: [0, -100, 100, 0],
            y: [0, 100, -100, 0],
            scale: [1, 0.9, 1.2, 1],
          }}
          transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-1/4 right-1/4 w-[45rem] h-[45rem] bg-[#e5c07b]/15 rounded-full blur-[120px]"
        />
        <motion.div
          animate={{
            x: [0, 120, -120, 0],
            y: [0, 80, -80, 0],
            scale: [1, 1.2, 0.8, 1],
          }}
          transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[35rem] h-[35rem] bg-[#48484a]/30 rounded-full blur-[90px]"
        />
      </div>

      <div className="relative z-10 w-full min-h-screen flex items-center justify-center p-4">
        <InterviewLayout />
      </div>
    </div>
  );
}

export default App;
