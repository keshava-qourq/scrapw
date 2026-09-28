import { animate, useReducedMotion } from "motion/react";
import { useLayoutEffect, useRef } from "react";
import { EASE } from "./motion";

function format(value: number): string {
  return Math.round(value).toLocaleString("en-IN");
}

/** Counts from the previous value to the new one. Text is written directly, so React never fights the tween. */
export default function AnimatedNumber({ value, className }: { value: number; className?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const previous = useRef(0);
  const reduceMotion = useReducedMotion();

  useLayoutEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (reduceMotion) {
      node.textContent = format(value);
      previous.current = value;
      return;
    }
    node.textContent = format(previous.current);
    const controls = animate(previous.current, value, {
      duration: 1.3,
      ease: EASE,
      onUpdate: (latest) => {
        node.textContent = format(latest);
      },
    });
    previous.current = value;
    return () => controls.stop();
  }, [value, reduceMotion]);

  return <span ref={ref} className={`tabular-nums ${className ?? ""}`} />;
}
