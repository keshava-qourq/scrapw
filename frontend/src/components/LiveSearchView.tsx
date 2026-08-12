import { useEffect, useState, type FormEvent } from "react";
import { createCard, listCards, searchLive } from "../api";
import LiveProductCard from "./LiveProductCard";
import LiveFiltersPopup, { type LiveFilters } from "./LiveFiltersPopup";
import Pagination from "./Pagination";
import type { Card, LiveSearchResponse, LiveSortOption } from "../types";
import { LIVE_SORT_OPTIONS } from "../types";

const NEW_CARD_FORM = { bank_name: "", card_name: "" };

export default function LiveSearchView() {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<LiveSortOption>("relevance");
  const [filters, setFilters] = useState<LiveFilters>({});
  const [page, setPage] = useState(1);
  const [result, setResult] = useState<LiveSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const [cards, setCards] = useState<Card[]>([]);
  const [cardId, setCardId] = useState<string>("");
  const [showAddCard, setShowAddCard] = useState(false);
  const [newCard, setNewCard] = useState(NEW_CARD_FORM);

  useEffect(() => {
    listCards()
      .then(setCards)
      .catch(() => {
        /* card list is a nice-to-have; a failure here shouldn't block search */
      });
  }, []);

  async function runSearch(
    q: string,
    targetPage: number,
    targetSort: LiveSortOption,
    targetCardId: string,
    targetFilters: LiveFilters,
  ) {
    setHasSearched(true);
    setLoading(true);
    setError(null);
    try {
      const res = await searchLive({
        q,
        page: targetPage,
        limit: 20,
        sort: targetSort,
        card_id: targetCardId || undefined,
        marketplace: targetFilters.marketplace,
        min_price: targetFilters.min_price,
        max_price: targetFilters.max_price,
        min_rating: targetFilters.min_rating,
      });
      setResult(res);
      setPage(targetPage);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed) runSearch(trimmed, 1, sort, cardId, filters);
  }

  function handleSortChange(newSort: LiveSortOption) {
    setSort(newSort);
    if (result) runSearch(result.query, 1, newSort, cardId, filters);
  }

  function handleCardChange(newCardId: string) {
    setCardId(newCardId);
    if (result) runSearch(result.query, 1, sort, newCardId, filters);
  }

  function handleFiltersApply(newFilters: LiveFilters) {
    setFilters(newFilters);
    if (result) runSearch(result.query, 1, sort, cardId, newFilters);
  }

  async function handleAddCard(e: FormEvent) {
    e.preventDefault();
    if (!newCard.bank_name.trim() || !newCard.card_name.trim()) return;
    try {
      const card = await createCard({
        bank_name: newCard.bank_name.trim(),
        card_name: newCard.card_name.trim(),
        card_type: "credit",
      });
      setCards((c) => [...c, card]);
      setCardId(card.id);
      setNewCard(NEW_CARD_FORM);
      setShowAddCard(false);
      if (result) runSearch(result.query, 1, sort, card.id, filters);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add card");
    }
  }

  const unavailableProviders = result
    ? Object.entries(result.marketplace_status).filter(([, status]) => status !== "success")
    : [];
  const noProvidersEnabled = result != null && Object.keys(result.marketplace_status).length === 0;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <form onSubmit={handleSubmit} className="mb-3 flex w-full gap-3">
        <div className="relative flex-1">
          <svg
            className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z" />
          </svg>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search any product, e.g. iPhone 17 under 80000"
            className="w-full rounded-xl border border-slate-200 bg-white py-3.5 pl-12 pr-4 text-base text-slate-900 shadow-sm outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100"
          />
        </div>
        <button
          type="submit"
          className="rounded-xl bg-indigo-600 px-6 py-3.5 font-medium text-white shadow-sm transition hover:bg-indigo-500 active:bg-indigo-700"
        >
          Search
        </button>
      </form>

      <div className="mb-6 flex flex-wrap items-center gap-2">
        <svg className="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-9-9.75h18A1.5 1.5 0 0121.75 8.25v9A1.5 1.5 0 0120.25 18.75H3.75A1.5 1.5 0 012.25 17.25v-9A1.5 1.5 0 013.75 6.75z" />
        </svg>
        <select
          value={cardId}
          onChange={(e) => handleCardChange(e.target.value)}
          className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-700 outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
        >
          <option value="">No card selected</option>
          {cards.map((c) => (
            <option key={c.id} value={c.id}>
              {c.bank_name} {c.card_name}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={() => setShowAddCard((v) => !v)}
          className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          + Add card
        </button>
        <LiveFiltersPopup filters={filters} onApply={handleFiltersApply} />
      </div>

      {showAddCard && (
        <form onSubmit={handleAddCard} className="mb-6 flex flex-wrap items-end gap-2 rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Bank</label>
            <input
              type="text"
              placeholder="e.g. HDFC"
              value={newCard.bank_name}
              onChange={(e) => setNewCard((f) => ({ ...f, bank_name: e.target.value }))}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-500">Card name</label>
            <input
              type="text"
              placeholder="e.g. Regalia"
              value={newCard.card_name}
              onChange={(e) => setNewCard((f) => ({ ...f, card_name: e.target.value }))}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
            />
          </div>
          <button
            type="submit"
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-500"
          >
            Add
          </button>
          <p className="w-full text-xs text-slate-400">
            Offers for a card are added via the API (see <code className="rounded bg-slate-100 px-1">/docs</code> →{" "}
            <code className="rounded bg-slate-100 px-1">POST /cards/{"{card_id}"}/offers</code>) — no offers yet means
            no discount will show for this card.
          </p>
        </form>
      )}

      {!hasSearched ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <p className="text-lg font-medium text-slate-700">Real results from across the web, via SerpApi</p>
          <p className="mt-1 text-sm text-slate-400">Try &ldquo;Samsung 55 inch 4K TV under 50000&rdquo;</p>
        </div>
      ) : (
        <>
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-slate-500">
              {result && (
                <>
                  <span className="font-medium text-slate-800">{result.total}</span> results for &ldquo;
                  <span className="font-medium text-slate-800">{result.query}</span>&rdquo;
                  {result.cache_hit && <span className="ml-2 text-xs text-slate-400">(cached)</span>}
                </>
              )}
            </p>
            <label className="flex items-center gap-2 text-sm text-slate-600">
              Sort by
              <select
                value={sort}
                onChange={(e) => handleSortChange(e.target.value as LiveSortOption)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
              >
                {LIVE_SORT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {noProvidersEnabled && (
            <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              No live data providers are enabled — set <code className="rounded bg-amber-100 px-1">SERPAPI_API_KEY</code> in
              the backend&rsquo;s <code className="rounded bg-amber-100 px-1">.env</code> to get real results.
            </div>
          )}
          {unavailableProviders.length > 0 && (
            <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
              {unavailableProviders.map(([name]) => name).join(", ")} unavailable for this search — showing results from
              other providers.
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
          )}

          {loading && (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="animate-pulse overflow-hidden rounded-2xl border border-slate-200 bg-white">
                  <div className="aspect-square bg-slate-100" />
                  <div className="space-y-2 p-4">
                    <div className="h-3 w-1/3 rounded bg-slate-100" />
                    <div className="h-4 w-full rounded bg-slate-100" />
                    <div className="h-4 w-2/3 rounded bg-slate-100" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {!loading && !error && result && result.results.length === 0 && (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-white py-16 text-center text-slate-400">
              No products found. Try a different search.
            </div>
          )}

          {!loading && !error && result && result.results.length > 0 && (
            <>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-4">
                {result.results.map((p) => (
                  <LiveProductCard key={p.id} product={p} />
                ))}
              </div>
              <Pagination
                page={page}
                pageSize={result.limit}
                total={result.total}
                onChange={(newPage) => runSearch(result.query, newPage, sort, cardId, filters)}
              />
            </>
          )}
        </>
      )}
    </div>
  );
}
