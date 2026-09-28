import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState, type FormEvent } from "react";
import { addWatchlistItem, deleteWatchlistItem, listWatchlistGroups } from "../api";
import type { WatchlistGroup } from "../types";
import Field from "./ui/Field";
import { ArrowUpRight, CloseIcon, StarIcon } from "./ui/icons";
import RevealText from "./ui/RevealText";
import RollText from "./ui/RollText";
import ScrambleText from "./ui/ScrambleText";
import { EASE } from "./ui/motion";

const EMPTY_FORM = {
  product_name: "",
  marketplace: "",
  price: "",
  rating: "",
  url: "",
  notes: "",
};

const eyebrow = "font-mono text-[11px] uppercase tracking-[0.2em] text-ash";
const rupees = (v: number) => `₹${v.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

export default function WatchlistView() {
  const [groups, setGroups] = useState<WatchlistGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);

  // Only the first load shows a placeholder; later refreshes swap data in place so rows can animate.
  async function refresh() {
    setError(null);
    try {
      setGroups(await listWatchlistGroups());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!form.product_name.trim() || !form.marketplace.trim() || !form.price || !form.url.trim()) return;

    setSubmitting(true);
    setError(null);
    try {
      await addWatchlistItem({
        product_name: form.product_name.trim(),
        marketplace: form.marketplace.trim(),
        price: Number(form.price),
        rating: form.rating ? Number(form.rating) : undefined,
        url: form.url.trim(),
        notes: form.notes.trim() || undefined,
      });
      setForm(EMPTY_FORM);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add item");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteWatchlistItem(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete item");
    }
  }

  const set = (key: keyof typeof EMPTY_FORM) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  return (
    <div className="mx-auto max-w-[1400px] px-4 pt-10 sm:px-8 sm:pt-16">
      <div className={`flex items-center justify-between ${eyebrow}`}>
        <ScrambleText text="(04) — Price board" />
        <span className="hidden sm:inline">
          {groups.length} product{groups.length === 1 ? "" : "s"} tracked
        </span>
      </div>
      <h1 className="mt-6 text-[clamp(3rem,9vw,8.5rem)] font-medium leading-[0.86] tracking-[-0.06em]">
        <span className="block">
          <RevealText text="Log it." />
        </span>
        <span className="block">
          <RevealText text="Compare" delay={0.18} />{" "}
          <RevealText text="it." delay={0.26} className="font-serif font-normal italic tracking-[-0.025em]" />
        </span>
      </h1>

      <div className="mt-14 grid gap-14 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] lg:gap-20">
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 1, ease: EASE }}
          className="h-fit lg:sticky lg:top-24"
        >
          <p className="max-w-sm text-[15px] leading-relaxed text-ash">
            Found a price somewhere? Log it under the same product name each time — entries are grouped and ranked,
            with the cheapest and best-rated called out.
          </p>
          <div className="mt-8 grid grid-cols-2 gap-x-6 gap-y-5">
            <Field label="Product name, e.g. iPhone 15 128GB" value={form.product_name} onChange={set("product_name")} required containerClassName="col-span-2" />
            <Field label="Marketplace" value={form.marketplace} onChange={set("marketplace")} required />
            <Field label="Price ₹" type="number" min={0} step="0.01" value={form.price} onChange={set("price")} required />
            <Field label="Rating (0–5)" type="number" min={0} max={5} step="0.1" value={form.rating} onChange={set("rating")} />
            <Field label="Product URL" type="url" value={form.url} onChange={set("url")} required />
            <Field label="Notes (optional)" value={form.notes} onChange={set("notes")} containerClassName="col-span-2" />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="group mt-8 h-14 w-full rounded-full bg-ink text-[15px] font-medium text-paper transition-colors duration-500 hover:bg-acid hover:text-ink disabled:opacity-60"
          >
            <RollText>{submitting ? "Adding…" : "Add price"}</RollText>
          </button>
          <AnimatePresence>
            {error && (
              <motion.p
                role="alert"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 overflow-hidden border-l-2 border-ember pl-3 text-sm text-ember"
              >
                {error}
              </motion.p>
            )}
          </AnimatePresence>
        </motion.form>

        <div>
          {loading ? (
            <div className="space-y-10">
              {[0, 1].map((i) => (
                <div key={i} className="border-t border-ink pt-6">
                  <div className="h-8 w-1/2 rounded-full bg-bone" />
                  <div className="mt-6 h-3 w-full rounded-full bg-bone" />
                  <div className="mt-4 h-3 w-4/5 rounded-full bg-bone" />
                </div>
              ))}
            </div>
          ) : groups.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 1 }}
              className="flex min-h-[320px] flex-col justify-center border-t border-ink pt-10"
            >
              <p className="font-serif text-5xl italic tracking-[-0.02em] sm:text-6xl">Nothing here yet.</p>
              <p className="mt-4 max-w-sm text-[15px] text-ash">Add your first price on the left and it&rsquo;ll show up here.</p>
            </motion.div>
          ) : (
            <div className="space-y-16">
              <AnimatePresence initial={false}>
                {groups.map((group, gi) => (
                  <PriceGroup key={group.group_key} group={group} index={gi} onDelete={handleDelete} />
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PriceGroup({
  group,
  index,
  onDelete,
}: {
  group: WatchlistGroup;
  index: number;
  onDelete: (id: string) => void;
}) {
  const prices = group.items.map((i) => i.price);
  const maxPrice = Math.max(...prices);
  const minPrice = Math.min(...prices);
  const saving = group.items.length > 1 ? maxPrice - minPrice : 0;

  return (
    <motion.section
      layout
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -40 }}
      viewport={{ once: true, margin: "0px 0px -10% 0px" }}
      transition={{ duration: 0.9, ease: EASE, delay: Math.min(index, 3) * 0.08 }}
      className="border-t border-ink pt-6"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-2">
        <h2 className="text-3xl font-medium tracking-[-0.04em] sm:text-4xl">{group.product_name}</h2>
        <span className={eyebrow}>
          {group.items.length} price{group.items.length === 1 ? "" : "s"}
          {saving > 0 && <span className="ml-3 rounded-full bg-acid px-2 py-0.5 text-ink">Save {rupees(saving)}</span>}
        </span>
      </div>

      <ul className="mt-6">
        <AnimatePresence initial={false}>
          {group.items.map((item, i) => {
            const isCheapest = item.id === group.lowest_price_item_id;
            const isBestRated = item.id === group.highest_rated_item_id;
            return (
              <motion.li
                key={item.id}
                layout
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0, x: -30 }}
                transition={{ duration: 0.6, ease: EASE }}
                className="group overflow-hidden border-b border-line"
              >
                <div className="grid grid-cols-[1fr_auto] items-center gap-x-6 gap-y-3 py-4 sm:grid-cols-[minmax(0,180px)_1fr_auto]">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="truncate text-[15px] font-medium capitalize">{item.marketplace}</span>
                      {isBestRated && item.rating != null && (
                        <span className="flex items-center gap-1 font-mono text-[11px] text-ash">
                          <StarIcon className="h-3 w-3 text-ink" />
                          {item.rating.toFixed(1)}
                        </span>
                      )}
                    </div>
                    <div className="mt-1 flex flex-wrap gap-1.5">
                      {isCheapest && (
                        <span className="rounded-full bg-acid px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.14em]">Best price</span>
                      )}
                      {isBestRated && (
                        <span className="rounded-full border border-ink px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.14em]">Top rated</span>
                      )}
                    </div>
                  </div>

                  <div className="col-span-2 row-start-2 sm:col-span-1 sm:row-start-auto">
                    <div className="h-2 w-full overflow-hidden rounded-full bg-bone">
                      <motion.div
                        initial={{ scaleX: 0 }}
                        whileInView={{ scaleX: item.price / maxPrice }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.3, ease: EASE, delay: 0.2 + i * 0.08 }}
                        className={`h-full origin-left rounded-full ${isCheapest ? "bg-acid" : "bg-ink/80"}`}
                      />
                    </div>
                    {item.notes && <p className="mt-2 truncate text-xs text-ash">{item.notes}</p>}
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-xl font-medium tracking-[-0.02em] tabular-nums">{rupees(item.price)}</span>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`Open ${item.marketplace} listing`}
                      className="flex h-9 w-9 items-center justify-center rounded-full border border-line transition-colors hover:border-ink hover:bg-ink hover:text-paper"
                    >
                      <ArrowUpRight className="h-3.5 w-3.5" />
                    </a>
                    <button
                      onClick={() => onDelete(item.id)}
                      aria-label={`Remove ${item.marketplace} price`}
                      className="flex h-9 w-9 items-center justify-center rounded-full text-ash transition-colors hover:bg-ember hover:text-paper sm:opacity-0 sm:group-hover:opacity-100 sm:focus-visible:opacity-100"
                    >
                      <CloseIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </motion.li>
            );
          })}
        </AnimatePresence>
      </ul>
    </motion.section>
  );
}
