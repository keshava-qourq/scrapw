import { useEffect, useState, type FormEvent } from "react";
import { addWatchlistItem, deleteWatchlistItem, listWatchlistGroups } from "../api";
import type { WatchlistGroup } from "../types";

const EMPTY_FORM = {
  product_name: "",
  marketplace: "",
  price: "",
  rating: "",
  url: "",
  notes: "",
};

export default function WatchlistView() {
  const [groups, setGroups] = useState<WatchlistGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);

  async function refresh() {
    setLoading(true);
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

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-slate-900">Price watchlist</h1>
        <p className="mt-1 text-sm text-slate-500">
          Log a price you found on any site, under the same product name each time, and it'll be grouped
          and ranked automatically — cheapest and best-rated highlighted.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="mb-8 grid grid-cols-1 gap-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:grid-cols-2"
      >
        <input
          type="text"
          placeholder="Product name, e.g. iPhone 15 128GB"
          value={form.product_name}
          onChange={(e) => setForm((f) => ({ ...f, product_name: e.target.value }))}
          required
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 sm:col-span-2"
        />
        <input
          type="text"
          placeholder="Marketplace, e.g. Amazon"
          value={form.marketplace}
          onChange={(e) => setForm((f) => ({ ...f, marketplace: e.target.value }))}
          required
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
        />
        <input
          type="number"
          min={0}
          step="0.01"
          placeholder="Price (₹)"
          value={form.price}
          onChange={(e) => setForm((f) => ({ ...f, price: e.target.value }))}
          required
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
        />
        <input
          type="number"
          min={0}
          max={5}
          step="0.1"
          placeholder="Rating (optional, 0-5)"
          value={form.rating}
          onChange={(e) => setForm((f) => ({ ...f, rating: e.target.value }))}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
        />
        <input
          type="url"
          placeholder="Product URL"
          value={form.url}
          onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))}
          required
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
        />
        <input
          type="text"
          placeholder="Notes (optional)"
          value={form.notes}
          onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 sm:col-span-2"
        />
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-500 disabled:opacity-50 sm:col-span-2"
        >
          {submitting ? "Adding…" : "Add price"}
        </button>
      </form>

      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
      )}

      {loading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : groups.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white py-16 text-center text-slate-400">
          No prices logged yet. Add one above to start comparing.
        </div>
      ) : (
        <div className="flex flex-col gap-6">
          {groups.map((group) => (
            <div key={group.group_key} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-100 px-5 py-3">
                <h2 className="text-sm font-semibold text-slate-800">{group.product_name}</h2>
              </div>
              <ul className="divide-y divide-slate-100">
                {group.items.map((item) => {
                  const isCheapest = item.id === group.lowest_price_item_id;
                  const isBestRated = item.id === group.highest_rated_item_id;
                  return (
                    <li key={item.id} className="flex items-center justify-between gap-4 px-5 py-3">
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-sm font-medium capitalize text-slate-800">{item.marketplace}</span>
                          {isCheapest && (
                            <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200">
                              Best price
                            </span>
                          )}
                          {isBestRated && (
                            <span className="rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700 ring-1 ring-inset ring-amber-200">
                              Top rated
                            </span>
                          )}
                        </div>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-0.5 block truncate text-xs text-indigo-500 hover:underline"
                        >
                          {item.url}
                        </a>
                        {item.notes && <p className="mt-0.5 text-xs text-slate-400">{item.notes}</p>}
                      </div>
                      <div className="flex shrink-0 items-center gap-4">
                        {item.rating != null && (
                          <span className="text-sm font-medium text-emerald-700">{item.rating.toFixed(1)}★</span>
                        )}
                        <span className="text-base font-semibold text-slate-900">
                          ₹{item.price.toLocaleString("en-IN")}
                        </span>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="text-slate-300 transition hover:text-red-500"
                          aria-label="Remove"
                        >
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
