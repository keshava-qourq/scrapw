import { animate, motion, useMotionValue, useTransform } from "motion/react";
import { useEffect } from "react";
import { markIntroSeen } from "./motion";

/** Full-screen counter 000 → 100, then the curtain lifts off the page. */
export default function Intro({ onDone }: { onDone: () => void }) {
  const count = useMotionValue(0);
  const label = useTransform(count, (v) => String(Math.round(v)).padStart(3, "0"));
  const barWidth = useTransform(count, (v) => `${v}%`);

  useEffect(() => {
    markIntroSeen();
    const controls = animate(count, 100, {
      duration: 1.7,
      ease: [0.65, 0, 0.35, 1],
      onComplete: () => window.setTimeout(onDone, 180),
    });
    return () => controls.stop();
  }, [count, onDone]);

  return (
    <motion.div
      className="fixed inset-0 z-[90] flex flex-col justify-between bg-ink p-6 text-paper sm:p-10"
      initial={{ clipPath: "inset(0 0 0% 0)" }}
      exit={{ clipPath: "inset(0 0 100% 0)" }}
      transition={{ duration: 1.05, ease: [0.76, 0, 0.24, 1] }}
    >
      <div className="flex justify-between font-mono text-[11px] uppercase tracking-[0.2em] text-paper/50">
        <span>ScrapW</span>
        <span>Warming up prices</span>
      </div>
      <div>
        <div className="flex items-end justify-between gap-6">
          <p className="font-serif text-[clamp(2.2rem,7vw,6rem)] italic leading-none text-acid">Every store.</p>
          <motion.span className="text-[clamp(5rem,22vw,19rem)] font-medium leading-[0.78] tracking-[-0.06em] tabular-nums">
            {label}
          </motion.span>
        </div>
        <div className="mt-6 h-px w-full bg-paper/15">
          <motion.div style={{ width: barWidth }} className="h-px bg-acid" />
        </div>
      </div>
    </motion.div>
  );
}
