import { motion, useMotionValue, useScroll, useSpring, useTransform, type MotionValue } from "motion/react";
import { useEffect } from "react";
import SpinBadge from "./ui/SpinBadge";
import { EASE } from "./ui/motion";

interface Tile {
  src: string;
  label: string;
  query: string;
  position: string;
  depth: number;
  scrollShift: number;
  delay: number;
}

const TILES: Tile[] = [
  { src: "/images/headphones.webp", label: "Audio", query: "wireless headphones", position: "right-0 top-0 w-[46%]", depth: 1, scrollShift: -90, delay: 0.45 },
  { src: "/images/sneakers.webp", label: "Sneakers", query: "sneakers", position: "right-[44%] top-[30%] w-[34%]", depth: 2.2, scrollShift: -210, delay: 0.6 },
  { src: "/images/watches.webp", label: "Watches", query: "analog watches", position: "right-[8%] top-[60%] w-[30%]", depth: 1.5, scrollShift: -40, delay: 0.75 },
];

function CollageTile({
  tile,
  pointerX,
  pointerY,
  onSelect,
}: {
  tile: Tile;
  pointerX: MotionValue<number>;
  pointerY: MotionValue<number>;
  onSelect: (query: string) => void;
}) {
  const { scrollY } = useScroll();
  const scrollOffset = useTransform(scrollY, [0, 900], [0, tile.scrollShift]);
  const x = useTransform(pointerX, (v) => v * 36 * tile.depth);
  const y = useTransform(pointerY, (v) => v * 36 * tile.depth);

  return (
    <motion.div style={{ y: scrollOffset }} className={`absolute ${tile.position}`}>
      <motion.button
        type="button"
        onClick={() => onSelect(tile.query)}
        data-cursor={`Shop ${tile.label}`}
        style={{ x, y }}
        className="group block w-full"
      >
        <motion.div
          initial={{ clipPath: "inset(100% 0 0 0)" }}
          animate={{ clipPath: "inset(0% 0 0 0)" }}
          transition={{ duration: 1.4, ease: EASE, delay: tile.delay }}
          className="relative aspect-[4/5] overflow-hidden rounded-[6px] bg-bone"
        >
          <motion.img
            src={tile.src}
            alt=""
            initial={{ scale: 1.4 }}
            animate={{ scale: 1 }}
            transition={{ duration: 1.8, ease: EASE, delay: tile.delay }}
            className="h-full w-full object-cover transition-[filter] duration-700 group-hover:saturate-[1.15]"
          />
          <span className="absolute bottom-3 left-3 rounded-full bg-paper/90 px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.14em] text-ink backdrop-blur">
            {tile.label}
          </span>
        </motion.div>
      </motion.button>
    </motion.div>
  );
}

/** Floating product photos beside the hero headline: they drift with the mouse and scroll at different depths. */
export default function HeroCollage({ onSelect }: { onSelect: (query: string) => void }) {
  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);
  const pointerX = useSpring(rawX, { stiffness: 60, damping: 18 });
  const pointerY = useSpring(rawY, { stiffness: 60, damping: 18 });

  useEffect(() => {
    function handleMove(e: PointerEvent) {
      if (e.pointerType !== "mouse") return;
      rawX.set(e.clientX / window.innerWidth - 0.5);
      rawY.set(e.clientY / window.innerHeight - 0.5);
    }
    window.addEventListener("pointermove", handleMove);
    return () => window.removeEventListener("pointermove", handleMove);
  }, [rawX, rawY]);

  return (
    <div className="absolute right-0 top-0 hidden h-[500px] w-[40%] lg:block">
      {TILES.map((tile) => (
        <CollageTile key={tile.src} tile={tile} pointerX={pointerX} pointerY={pointerY} onSelect={onSelect} />
      ))}
      <motion.div
        initial={{ scale: 0, rotate: -90 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ duration: 1.2, ease: EASE, delay: 1.1 }}
        className="pointer-events-none absolute right-[36%] top-[8%] rounded-full bg-acid"
      >
        <SpinBadge text="One search · Every store · " />
      </motion.div>
    </div>
  );
}
