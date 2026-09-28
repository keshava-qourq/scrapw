import { motion, useMotionValueEvent, useScroll, useSpring } from "motion/react";
import { useState } from "react";
import type { User } from "../types";
import { HomeIcon } from "./ui/icons";
import RollText from "./ui/RollText";
import Wordmark from "./ui/Wordmark";
import { EASE } from "./ui/motion";

export type Tab = "live" | "compare";

const TABS: { id: Tab; label: string }[] = [
  { id: "live", label: "Home" },
  { id: "compare", label: "Price board" },
];

interface Props {
  tab: Tab;
  onTabChange: (tab: Tab) => void;
  user: User;
  onLogout: () => void;
}

export default function Header({ tab, onTabChange, user, onLogout }: Props) {
  const { scrollY, scrollYProgress } = useScroll();
  const progress = useSpring(scrollYProgress, { stiffness: 140, damping: 30 });
  const [hidden, setHidden] = useState(false);

  // Tuck the header away while scrolling down, bring it back on any upward scroll.
  useMotionValueEvent(scrollY, "change", (latest) => {
    const previous = scrollY.getPrevious() ?? 0;
    setHidden(latest > previous && latest > 140);
  });

  return (
    <>
      <motion.div aria-hidden style={{ scaleX: progress }} className="fixed inset-x-0 top-0 z-[55] h-[2px] origin-left bg-ink" />
      <motion.header
        animate={{ y: hidden ? "-100%" : "0%" }}
        transition={{ duration: 0.5, ease: EASE }}
        className="sticky top-0 z-50 border-b border-line/80 bg-paper/75 backdrop-blur-xl"
      >
        <div className="mx-auto flex h-16 max-w-[1400px] items-center gap-4 px-4 sm:px-8">
          <button onClick={() => onTabChange("live")} aria-label="Go to home" className="shrink-0">
            <Wordmark />
          </button>

          <nav className="mx-auto flex items-center gap-1 rounded-full border border-line p-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => onTabChange(t.id)}
                className="relative rounded-full px-3.5 py-1.5 text-[13px] font-medium sm:px-4"
                aria-current={tab === t.id ? "page" : undefined}
              >
                {tab === t.id && (
                  <motion.span
                    layoutId="nav-pill"
                    className="absolute inset-0 rounded-full bg-ink"
                    transition={{ type: "spring", stiffness: 420, damping: 34 }}
                  />
                )}
                <span
                  className={`relative flex items-center gap-1.5 transition-colors duration-300 ${tab === t.id ? "text-paper" : "text-ash hover:text-ink"}`}
                >
                  {t.id === "live" && <HomeIcon className="h-3.5 w-3.5" />}
                  {t.label}
                </span>
              </button>
            ))}
          </nav>

          <div className="flex shrink-0 items-center gap-4">
            <span className="hidden max-w-[180px] truncate font-mono text-[11px] uppercase tracking-[0.14em] text-ash md:inline">
              {user.email}
            </span>
            <button onClick={onLogout} className="group text-[13px] font-medium">
              <RollText>Log out</RollText>
            </button>
          </div>
        </div>
      </motion.header>
    </>
  );
}
