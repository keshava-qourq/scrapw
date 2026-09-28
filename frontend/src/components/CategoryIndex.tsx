import { AnimatePresence, motion, useMotionValue, useSpring, useTransform, useVelocity } from "motion/react";
import { useRef, useState, type PointerEvent } from "react";
import { ArrowRight } from "./ui/icons";
import RollText from "./ui/RollText";
import ScrambleText from "./ui/ScrambleText";
import { EASE } from "./ui/motion";

const CATEGORIES = [
  { name: "Sneakers", query: "sneakers", image: "/images/sneakers.webp" },
  { name: "Watches", query: "analog watches", image: "/images/watches.webp" },
  { name: "Headphones", query: "wireless headphones", image: "/images/headphones.webp" },
  { name: "Cameras", query: "mirrorless camera", image: "/images/cameras.webp" },
  { name: "Sunglasses", query: "sunglasses", image: "/images/sunglasses.webp" },
  { name: "Smartwatches", query: "smartwatch", image: "/images/smartwatch.webp" },
];

const pad = (n: number) => String(n).padStart(2, "0");
const eyebrow = "font-mono text-[11px] uppercase tracking-[0.2em] text-ash";

/**
 * Big typographic category list. On mouse devices a photo preview trails the cursor,
 * tilting with its horizontal speed and wiping between categories.
 */
export default function CategoryIndex({ onSelect }: { onSelect: (query: string) => void }) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState<number | null>(null);
  const [previous, setPrevious] = useState<number | null>(null);

  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, { stiffness: 170, damping: 20, mass: 0.6 });
  const springY = useSpring(y, { stiffness: 170, damping: 20, mass: 0.6 });
  const rotate = useTransform(useVelocity(springX), [-1400, 0, 1400], [-12, 0, 12], { clamp: true });

  function handleMove(e: PointerEvent<HTMLDivElement>) {
    const rect = wrapperRef.current?.getBoundingClientRect();
    if (!rect) return;
    x.set(e.clientX - rect.left);
    y.set(e.clientY - rect.top);
  }

  function activate(index: number | null) {
    if (index === active) return;
    if (active !== null) setPrevious(active);
    setActive(index);
  }

  return (
    <section className="mx-auto max-w-[1400px] px-4 sm:px-8">
      <div className={`flex items-end justify-between ${eyebrow}`}>
        <ScrambleText text="(03) — Shop by category" />
        <span>{pad(CATEGORIES.length)} edits</span>
      </div>

      <div ref={wrapperRef} onPointerMove={handleMove} onPointerLeave={() => activate(null)} className="relative mt-10">
        <ul className="border-b border-line">
          {CATEGORIES.map((category, i) => (
            <motion.li
              key={category.name}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "0px 0px -8% 0px" }}
              transition={{ duration: 0.9, ease: EASE, delay: i * 0.05 }}
              className="border-t border-line"
            >
              <button
                type="button"
                onClick={() => onSelect(category.query)}
                onPointerEnter={() => activate(i)}
                onFocus={() => activate(i)}
                data-cursor="Shop"
                className={`group grid w-full grid-cols-[2.5rem_1fr_auto] items-center gap-3 py-4 text-left transition-opacity duration-500 sm:grid-cols-[5rem_1fr_auto] sm:py-6 ${
                  active !== null && active !== i ? "pointer-fine:opacity-35" : ""
                }`}
              >
                <span className="font-mono text-[11px] tracking-[0.2em] text-ash">{pad(i + 1)}</span>
                <span className="text-[clamp(2.1rem,7.2vw,6.5rem)] font-medium leading-none tracking-[-0.055em] transition-transform duration-700 ease-expo group-hover:translate-x-3 sm:group-hover:translate-x-8">
                  <RollText
                    className="-mb-[0.14em] pb-[0.14em]"
                    hoverClassName="font-serif font-normal italic tracking-[-0.02em]"
                  >
                    {category.name}
                  </RollText>
                </span>
                <span className="flex items-center gap-3">
                  <img
                    src={category.image}
                    alt=""
                    loading="lazy"
                    className="hidden h-16 w-13 rounded-[4px] object-cover pointer-coarse:block"
                  />
                  <span className="flex h-11 w-11 items-center justify-center rounded-full border border-line transition-all duration-500 ease-expo group-hover:-rotate-45 group-hover:border-ink group-hover:bg-ink group-hover:text-paper sm:h-14 sm:w-14">
                    <ArrowRight className="h-5 w-5" />
                  </span>
                </span>
              </button>
            </motion.li>
          ))}
        </ul>

        <motion.div
          aria-hidden
          style={{ x: springX, y: springY, rotate }}
          className="pointer-events-none absolute left-0 top-0 z-10 hidden pointer-fine:block"
        >
          <AnimatePresence>
            {active !== null && (
              <motion.div
                initial={{ scale: 0.3, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.3, opacity: 0 }}
                transition={{ duration: 0.55, ease: EASE }}
                className="relative h-80 w-64 -translate-x-1/2 -translate-y-1/2 overflow-hidden rounded-[6px] bg-bone shadow-[0_30px_80px_-20px_rgba(13,13,12,0.45)]"
              >
                {CATEGORIES.map((category, i) => {
                  const isActive = i === active;
                  const isPrevious = i === previous;
                  return (
                    <motion.img
                      key={category.name}
                      src={category.image}
                      alt=""
                      initial={false}
                      animate={{
                        clipPath: isActive || isPrevious ? "inset(0% 0 0 0)" : "inset(100% 0 0 0)",
                        scale: isActive ? 1 : 1.25,
                      }}
                      transition={isActive ? { duration: 0.75, ease: EASE } : { duration: 0 }}
                      style={{ zIndex: isActive ? 2 : isPrevious ? 1 : 0 }}
                      className="absolute inset-0 h-full w-full object-cover"
                    />
                  );
                })}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </section>
  );
}
