import { motion } from "motion/react";
import { EASE } from "./motion";

interface Props {
  text: string;
  className?: string;
  delay?: number;
  stagger?: number;
}

/** Each word slides up out of its own mask, one after another. */
export default function RevealText({ text, className, delay = 0, stagger = 0.07 }: Props) {
  const words = text.split(" ");
  return (
    <span className={className} aria-label={text} role="text">
      {words.map((word, i) => (
        <span key={`${word}-${i}`} aria-hidden className="inline-block overflow-hidden pb-[0.1em] align-bottom">
          <motion.span
            className="inline-block"
            initial={{ y: "110%" }}
            animate={{ y: "0%" }}
            transition={{ duration: 1.1, ease: EASE, delay: delay + i * stagger }}
          >
            {word}
            {i < words.length - 1 && " "}
          </motion.span>
        </span>
      ))}
    </span>
  );
}
