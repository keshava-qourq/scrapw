import { motion } from "motion/react";
import { ArrowRight } from "./ui/icons";
import Magnetic from "./ui/Magnetic";
import { EASE, scrollToTop } from "./ui/motion";

const WORD = "scrapw";

export default function Footer() {
  return (
    <footer className="mt-32 overflow-hidden border-t border-line">
      <div className="mx-auto flex max-w-[1400px] flex-col justify-between gap-6 px-4 py-8 sm:flex-row sm:items-center sm:px-8">
        <div className="flex flex-col gap-2 font-mono text-[10px] uppercase tracking-[0.18em] text-ash">
          <span>Prices via licensed data providers · Not affiliated with any marketplace</span>
          <span>Category photography via Unsplash · © {new Date().getFullYear()} ScrapW</span>
        </div>
        <Magnetic>
          <button
            onClick={scrollToTop}
            data-cursor="Top"
            aria-label="Back to top"
            className="group flex h-14 w-14 items-center justify-center rounded-full border border-ink transition-colors duration-300 hover:bg-ink hover:text-paper"
          >
            <ArrowRight className="h-5 w-5 -rotate-90 transition-transform duration-500 ease-expo group-hover:-translate-y-0.5" />
          </button>
        </Magnetic>
      </div>
      <motion.p
        aria-hidden
        initial={{ y: "45%" }}
        whileInView={{ y: "14%" }}
        viewport={{ once: true, margin: "0px 0px -10% 0px" }}
        transition={{ duration: 1.4, ease: EASE }}
        className="flex select-none justify-center font-serif text-[31vw] italic leading-[0.72] tracking-[-0.05em] text-ink"
      >
        {WORD.split("").map((letter, i) => (
          <motion.span
            key={i}
            whileHover={{ y: "-12%", color: "#d4ff3f" }}
            transition={{ type: "spring", stiffness: 380, damping: 14 }}
            className="inline-block"
          >
            {letter}
          </motion.span>
        ))}
      </motion.p>
    </footer>
  );
}
