import Lenis from "lenis";
import { useEffect, useState } from "react";

/** Expo-out: fast start, long soft landing. Used for nearly every transition. */
export const EASE: [number, number, number, number] = [0.16, 1, 0.3, 1];

let lenis: Lenis | null = null;

function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** Start inertial page scrolling. Returns a cleanup function. No-op for reduced-motion users. */
export function startSmoothScroll(): () => void {
  if (prefersReducedMotion()) return () => {};
  lenis = new Lenis({ autoRaf: true, lerp: 0.09 });
  return () => {
    lenis?.destroy();
    lenis = null;
  };
}

/** Freeze page scroll while a modal/drawer is open. */
export function lockScroll(locked: boolean): void {
  if (lenis) {
    if (locked) lenis.stop();
    else lenis.start();
  }
  document.documentElement.style.overflow = locked ? "hidden" : "";
}

export function scrollToTop(): void {
  if (lenis) lenis.scrollTo(0);
  else window.scrollTo({ top: 0, behavior: prefersReducedMotion() ? "auto" : "smooth" });
}

/** Index that advances through `length` items every `intervalMs`. */
export function useCycle(length: number, intervalMs: number): number {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    const timer = window.setInterval(() => setIndex((i) => (i + 1) % length), intervalMs);
    return () => window.clearInterval(timer);
  }, [length, intervalMs]);
  return index;
}

const INTRO_KEY = "scrapw.introSeen";

/** The intro plays once per browser session, and never for reduced-motion users. Read-only. */
export function shouldPlayIntro(): boolean {
  if (prefersReducedMotion()) return false;
  try {
    return !sessionStorage.getItem(INTRO_KEY);
  } catch {
    return true;
  }
}

export function markIntroSeen(): void {
  try {
    sessionStorage.setItem(INTRO_KEY, "1");
  } catch {
    // Storage blocked — the intro will just play again next load.
  }
}
