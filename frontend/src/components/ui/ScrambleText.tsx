import { useInView, useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";

const GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/—+*";
const FRAMES = 20;

/** Monospace label that resolves from random glyphs, left to right, the first time it scrolls into view. */
export default function ScrambleText({ text, className }: { text: string; className?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const reduceMotion = useReducedMotion();
  const [output, setOutput] = useState(text);

  useEffect(() => {
    if (!inView || reduceMotion) return;
    let frame = 0;
    const timer = window.setInterval(() => {
      frame += 1;
      const resolved = Math.floor((frame / FRAMES) * text.length);
      setOutput(
        text
          .split("")
          .map((ch, i) => (ch === " " || i < resolved ? ch : GLYPHS[Math.floor(Math.random() * GLYPHS.length)]))
          .join(""),
      );
      if (frame >= FRAMES) window.clearInterval(timer);
    }, 34);
    return () => window.clearInterval(timer);
  }, [inView, reduceMotion, text]);

  return (
    <span ref={ref} className={className} aria-label={text}>
      <span aria-hidden>{output}</span>
    </span>
  );
}
