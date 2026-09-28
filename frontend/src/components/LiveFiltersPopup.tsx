import { AnimatePresence, motion, type Variants } from "motion/react";
import { useEffect, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import type { LiveMarketplace } from "../types";
import { LIVE_MARKETPLACES } from "../types";
import Field from "./ui/Field";
import { CloseIcon, SlidersIcon } from "./ui/icons";
import RollText from "./ui/RollText";
import { EASE, lockScroll } from "./ui/motion";

export interface LiveFilters {
  marketplace?: LiveMarketplace;
  min_price?: number;
  max_price?: number;
  min_rating?: number;
}

interface Props {
  filters: LiveFilters;
  onApply: (filters: LiveFilters) => void;
}

const EMPTY: LiveFilters = {};

function countActive(f: LiveFilters): number {
  return Object.values(f).filter((v) => v !== undefined).length;
}

const section: Variants = {
  closed: { opacity: 0, y: 24 },
  open: (i: number) => ({ opacity: 1, y: 0, transition: { delay: 0.18 + i * 0.07, duration: 0.7, ease: EASE } }),
};

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`rounded-full border px-4 py-2 text-[13px] transition-all duration-300 ease-expo ${
        active ? "border-ink bg-ink text-paper" : "border-line text-ink hover:border-ink"
      }`}
    >
      {children}
    </button>
  );
}

function SectionTitle({ n, children }: { n: string; children: ReactNode }) {
  return (
    <h3 className="mb-4 flex items-baseline gap-3 text-[15px] font-medium">
      <span className="font-mono text-[10px] tracking-[0.16em] text-ash">{n}</span>
      {children}
    </h3>
  );
}

/** Filters live in a slide-over drawer from the right. */
export default function LiveFiltersPopup({ filters, onApply }: Props) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<LiveFilters>(filters);

  useEffect(() => {
    if (open) setDraft(filters);
  }, [open, filters]);

  useEffect(() => {
    if (!open) return;
    lockScroll(true);
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", handleKey);
    return () => {
      lockScroll(false);
      document.removeEventListener("keydown", handleKey);
    };
  }, [open]);

  const activeCount = countActive(filters);

  function apply() {
    onApply(draft);
    setOpen(false);
  }

  function reset() {
    setDraft(EMPTY);
    onApply(EMPTY);
    setOpen(false);
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex h-10 items-center gap-2 rounded-full border border-line px-4 text-[13px] font-medium transition-colors duration-300 hover:border-ink"
      >
        <SlidersIcon />
        Filters
        <AnimatePresence>
          {activeCount > 0 && (
            <motion.span
              key={activeCount}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ type: "spring", stiffness: 500, damping: 22 }}
              className="flex h-5 min-w-5 items-center justify-center rounded-full bg-acid px-1 font-mono text-[10px]"
            >
              {activeCount}
            </motion.span>
          )}
        </AnimatePresence>
      </button>

      {/* Portaled so ancestors' transforms/filters (page transitions) can't trap the fixed overlay. */}
      {createPortal(
      <AnimatePresence>
        {open && (
          <motion.div className="fixed inset-0 z-[80]" initial="closed" animate="open" exit="closed">
            <motion.div
              className="absolute inset-0 bg-ink/40 backdrop-blur-sm"
              variants={{ closed: { opacity: 0 }, open: { opacity: 1 } }}
              transition={{ duration: 0.5 }}
              onClick={() => setOpen(false)}
            />
            <motion.aside
              role="dialog"
              aria-modal="true"
              aria-label="Filters"
              data-lenis-prevent
              variants={{ closed: { x: "100%" }, open: { x: "0%" } }}
              transition={{ type: "spring", stiffness: 240, damping: 32 }}
              className="absolute inset-y-0 right-0 flex w-full max-w-md flex-col bg-paper shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-line px-6 py-5">
                <h2 className="font-serif text-4xl italic tracking-[-0.02em]">Filters</h2>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  aria-label="Close filters"
                  className="group flex h-11 w-11 items-center justify-center rounded-full border border-line transition-colors duration-300 hover:border-ink hover:bg-ink hover:text-paper"
                >
                  <CloseIcon className="h-5 w-5 transition-transform duration-500 ease-expo group-hover:rotate-90" />
                </button>
              </div>

              <div className="flex-1 space-y-12 overflow-y-auto px-6 py-10">
                <motion.section variants={section} custom={0}>
                  <SectionTitle n="01">Marketplace</SectionTitle>
                  <div className="flex flex-wrap gap-2">
                    {LIVE_MARKETPLACES.map((mp) => (
                      <Chip
                        key={mp}
                        active={draft.marketplace === mp}
                        onClick={() => setDraft((d) => ({ ...d, marketplace: d.marketplace === mp ? undefined : mp }))}
                      >
                        {mp === "AJIO" ? "AJIO" : mp.charAt(0) + mp.slice(1).toLowerCase()}
                      </Chip>
                    ))}
                  </div>
                </motion.section>

                <motion.section variants={section} custom={1}>
                  <SectionTitle n="02">Price range</SectionTitle>
                  <div className="grid grid-cols-2 gap-6">
                    <Field
                      label="Min ₹"
                      type="number"
                      min={0}
                      value={draft.min_price ?? ""}
                      onChange={(e) =>
                        setDraft((d) => ({ ...d, min_price: e.target.value ? Number(e.target.value) : undefined }))
                      }
                    />
                    <Field
                      label="Max ₹"
                      type="number"
                      min={0}
                      value={draft.max_price ?? ""}
                      onChange={(e) =>
                        setDraft((d) => ({ ...d, max_price: e.target.value ? Number(e.target.value) : undefined }))
                      }
                    />
                  </div>
                </motion.section>

                <motion.section variants={section} custom={2}>
                  <SectionTitle n="03">Minimum rating</SectionTitle>
                  <div className="flex flex-wrap gap-2">
                    {[3, 3.5, 4, 4.5].map((r) => (
                      <Chip
                        key={r}
                        active={draft.min_rating === r}
                        onClick={() => setDraft((d) => ({ ...d, min_rating: d.min_rating === r ? undefined : r }))}
                      >
                        {r}+ ★
                      </Chip>
                    ))}
                  </div>
                </motion.section>
              </div>

              <div className="flex gap-3 border-t border-line px-6 py-5">
                <button
                  type="button"
                  onClick={reset}
                  className="h-12 rounded-full border border-line px-6 text-[14px] font-medium transition-colors hover:border-ink"
                >
                  Reset
                </button>
                <button
                  type="button"
                  onClick={apply}
                  className="group h-12 flex-1 rounded-full bg-ink text-[14px] font-medium text-paper transition-colors duration-500 hover:bg-acid hover:text-ink"
                >
                  <RollText>Show results</RollText>
                </button>
              </div>
            </motion.aside>
          </motion.div>
        )}
      </AnimatePresence>,
      document.body,
      )}
    </>
  );
}
