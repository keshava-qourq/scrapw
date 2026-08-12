import { useEffect, useRef, useState } from "react";
import type { LiveMarketplace } from "../types";
import { LIVE_MARKETPLACES } from "../types";

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

export default function LiveFiltersPopup({ filters, onApply }: Props) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<LiveFilters>(filters);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) setDraft(filters);
  }, [open, filters]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
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
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
      >
        <svg className="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m9 12h3.75M16.5 18a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0M3.75 18H13.5m-9-6h9.75m-9.75 0a1.5 1.5 0 003 0m-3 0a1.5 1.5 0 013 0m9.75 0H21" />
        </svg>
        Filters
        {activeCount > 0 && (
          <span className="flex h-4 w-4 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-semibold text-white">
            {activeCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute left-0 z-20 mt-2 w-72 rounded-2xl border border-slate-200 bg-white p-4 shadow-lg">
          <div className="mb-3">
            <h3 className="mb-2 text-sm font-semibold text-slate-800">Marketplace</h3>
            <div className="flex flex-wrap gap-1.5">
              {LIVE_MARKETPLACES.map((mp) => (
                <button
                  key={mp}
                  type="button"
                  onClick={() => setDraft((d) => ({ ...d, marketplace: d.marketplace === mp ? undefined : mp }))}
                  className={`rounded-full border px-2.5 py-1 text-xs font-medium capitalize transition ${
                    draft.marketplace === mp
                      ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                      : "border-slate-200 text-slate-600 hover:border-slate-300"
                  }`}
                >
                  {mp}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-3">
            <h3 className="mb-2 text-sm font-semibold text-slate-800">Price range (₹)</h3>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min={0}
                value={draft.min_price ?? ""}
                onChange={(e) => setDraft((d) => ({ ...d, min_price: e.target.value ? Number(e.target.value) : undefined }))}
                placeholder="Min"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
              />
              <span className="text-slate-400">–</span>
              <input
                type="number"
                min={0}
                value={draft.max_price ?? ""}
                onChange={(e) => setDraft((d) => ({ ...d, max_price: e.target.value ? Number(e.target.value) : undefined }))}
                placeholder="Max"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
              />
            </div>
          </div>

          <div className="mb-4">
            <h3 className="mb-2 text-sm font-semibold text-slate-800">Minimum rating</h3>
            <div className="flex gap-1.5">
              {[3, 3.5, 4, 4.5].map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setDraft((d) => ({ ...d, min_rating: d.min_rating === r ? undefined : r }))}
                  className={`rounded-full border px-2.5 py-1 text-xs font-medium transition ${
                    draft.min_rating === r
                      ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                      : "border-slate-200 text-slate-600 hover:border-slate-300"
                  }`}
                >
                  {r}+★
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between gap-2">
            <button type="button" onClick={reset} className="text-sm font-medium text-slate-500 hover:text-slate-700">
              Reset
            </button>
            <button
              type="button"
              onClick={apply}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-500"
            >
              Apply filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
