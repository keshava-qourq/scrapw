import { AnimatePresence, motion, useMotionValue, useSpring } from "motion/react";
import { useEffect, useState } from "react";

function supportsFollower(): boolean {
  return (
    window.matchMedia("(pointer: fine)").matches && !window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

/**
 * A label bubble that trails the mouse over any element with `data-cursor="Label"`.
 * It never replaces the system cursor, so nothing is lost for keyboard or touch users.
 */
export default function Cursor() {
  const [enabled] = useState(supportsFollower);
  const [label, setLabel] = useState<string | null>(null);
  const x = useMotionValue(-200);
  const y = useMotionValue(-200);
  const springX = useSpring(x, { stiffness: 450, damping: 38, mass: 0.5 });
  const springY = useSpring(y, { stiffness: 450, damping: 38, mass: 0.5 });

  useEffect(() => {
    if (!enabled) return;
    function handleMove(e: PointerEvent) {
      x.set(e.clientX);
      y.set(e.clientY);
      const target = (e.target as Element | null)?.closest?.("[data-cursor]");
      setLabel(target ? target.getAttribute("data-cursor") : null);
    }
    function handleLeave() {
      setLabel(null);
    }
    window.addEventListener("pointermove", handleMove);
    document.addEventListener("pointerleave", handleLeave);
    return () => {
      window.removeEventListener("pointermove", handleMove);
      document.removeEventListener("pointerleave", handleLeave);
    };
  }, [enabled, x, y]);

  if (!enabled) return null;

  return (
    <motion.div aria-hidden className="pointer-events-none fixed left-0 top-0 z-[70]" style={{ x: springX, y: springY }}>
      <motion.div
        className="flex -translate-x-1/2 -translate-y-1/2 items-center justify-center overflow-hidden rounded-full bg-acid font-mono text-[11px] font-medium uppercase tracking-[0.14em] text-ink"
        initial={false}
        animate={{ width: label ? 92 : 0, height: label ? 92 : 0 }}
        transition={{ type: "spring", stiffness: 320, damping: 26 }}
      >
        <AnimatePresence mode="wait">
          {label && (
            <motion.span
              key={label}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5 }}
              transition={{ duration: 0.2 }}
              className="whitespace-nowrap"
            >
              {label}
            </motion.span>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
}
