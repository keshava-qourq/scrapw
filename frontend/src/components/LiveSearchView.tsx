import { AnimatePresence, motion } from "motion/react";
import { useEffect, useEffectEvent, useRef, useState, type FormEvent, type ReactNode } from "react";
import { createCard, listCards, searchLive } from "../api";
import CategoryIndex from "./CategoryIndex";
import HeroCollage from "./HeroCollage";
import HowItWorks from "./HowItWorks";
import LiveProductCard from "./LiveProductCard";
import LiveFiltersPopup, { type LiveFilters } from "./LiveFiltersPopup";
import Pagination from "./Pagination";
import type { Card, LiveSearchResponse, LiveSortOption } from "../types";
import { LIVE_SORT_OPTIONS } from "../types";
import AnimatedNumber from "./ui/AnimatedNumber";
import Field from "./ui/Field";
import { ArrowRight, ChevronDown, HomeIcon, PlusIcon, SearchIcon } from "./ui/icons";
import Magnetic from "./ui/Magnetic";
import Marquee from "./ui/Marquee";
import RevealText from "./ui/RevealText";
import RollText from "./ui/RollText";
import ScrambleText from "./ui/ScrambleText";
import SpinBadge from "./ui/SpinBadge";
import { EASE, scrollToTop, useCycle } from "./ui/motion";

const NEW_CARD_FORM = { bank_name: "", card_name: "" };

const SUGGESTIONS = [
  "iPhone 17 under 80000",
  "Nike running shoes",
  "Samsung 55 inch 4K TV",
  "Levi's 511 slim jeans",
  "Sony WH-1000XM5",
];

const MARKETPLACES = ["Amazon", "Flipkart", "Myntra", "AJIO"];

// Desktop grid density: how many product columns to show at xl widths.
const DENSITY_CLASSES = { 2: "md:grid-cols-2", 3: "md:grid-cols-3", 4: "md:grid-cols-3 xl:grid-cols-4" } as const;
type Density = keyof typeof DENSITY_CLASSES;

const eyebrow = "font-mono text-[11px] uppercase tracking-[0.2em] text-ash";

interface Props {
  /** The search in the URL; null means the landing page. */
  routeQuery: string | null;
  routePage: number;
  /** Change the URL-level search. `replace` rewrites the current history entry instead of adding one. */
  onNavigate: (q: string | null, page: number, replace?: boolean) => void;
  onBack: () => void;
}

export default function LiveSearchView({ routeQuery, routePage, onNavigate, onBack }: Props) {
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

  const [density, setDensity] = useState<Density>(4);

  const suggestionIndex = useCycle(SUGGESTIONS.length, 2800);

  // "query|page" of the search currently shown/loading, so URL updates we caused ourselves don't refetch.
  const loadedKey = useRef<string | null>(null);
  // Bumped on every search (and on going home) so a slow, superseded response is ignored.
  const requestId = useRef(0);

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
    const id = ++requestId.current;
    loadedKey.current = `${q}|${targetPage}`;
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
      if (id !== requestId.current) return;
      setResult(res);
      setPage(targetPage);
    } catch (err) {
      if (id !== requestId.current) return;
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      if (id === requestId.current) setLoading(false);
    }
  }

  // The URL is the source of truth for which search is showing: typing a search, paging,
  // the Back button, browser back/forward and deep links all flow through here.
  // An effect event, so it reads the latest sort/card/filters without re-running when they change.
  const showRoute = useEffectEvent((routeQuery: string | null, routePage: number) => {
    if (!routeQuery) {
      requestId.current += 1;
      loadedKey.current = null;
      setHasSearched(false);
      setResult(null);
      setError(null);
      setLoading(false);
      setQuery("");
      setPage(1);
      return;
    }
    if (loadedKey.current === `${routeQuery}|${routePage}`) return;
    setQuery(routeQuery);
    scrollToTop();
    runSearch(routeQuery, routePage, sort, cardId, filters);
  });

  useEffect(() => {
    showRoute(routeQuery, routePage);
  }, [routeQuery, routePage]);

  /** Re-run the current search with new sort/card/filters, back on page 1. */
  function refine(targetSort: LiveSortOption, targetCardId: string, targetFilters: LiveFilters) {
    if (!routeQuery) return;
    runSearch(routeQuery, 1, targetSort, targetCardId, targetFilters);
    if (routePage !== 1) onNavigate(routeQuery, 1, true);
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    // An empty box searches whichever suggestion is currently showing.
    const trimmed = query.trim() || SUGGESTIONS[suggestionIndex];
    setQuery(trimmed);
    // Searching the same thing again (e.g. after an error) should refetch, not no-op.
    if (trimmed === routeQuery && routePage === 1) runSearch(trimmed, 1, sort, cardId, filters);
    else onNavigate(trimmed, 1);
  }

  function searchFor(text: string) {
    onNavigate(text, 1);
  }

  function handleSortChange(newSort: LiveSortOption) {
    setSort(newSort);
    refine(newSort, cardId, filters);
  }

  function handleCardChange(newCardId: string) {
    setCardId(newCardId);
    refine(sort, newCardId, filters);
  }

  function handleFiltersApply(newFilters: LiveFilters) {
    setFilters(newFilters);
    refine(sort, cardId, newFilters);
  }

  function handlePageChange(newPage: number) {
    if (routeQuery) onNavigate(routeQuery, newPage);
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
      refine(sort, card.id, filters);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add card");
    }
  }

  const unavailableProviders = result
    ? Object.entries(result.marketplace_status).filter(([, status]) => status !== "success")
    : [];
  const noProvidersEnabled = result != null && Object.keys(result.marketplace_status).length === 0;

  return (
    <div>
      <section className="mx-auto max-w-[1400px] px-4 pt-10 sm:px-8 sm:pt-16">
        <AnimatePresence initial={false}>
          {!hasSearched && (
            <motion.div
              key="hero"
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              transition={{ duration: 0.8, ease: EASE }}
              className="relative mb-12 overflow-hidden sm:mb-16 lg:mb-8 lg:min-h-[540px]"
            >
              <HeroCollage onSelect={searchFor} />
              <div className={`relative flex items-center justify-between ${eyebrow}`}>
                <ScrambleText text="(01) — Live price search" />
                <span className="hidden sm:inline lg:hidden">{MARKETPLACES.join(" / ")}</span>
              </div>
              <h1 className="relative mt-6 text-[clamp(3.4rem,11vw,10.5rem)] font-medium leading-[0.85] tracking-[-0.06em]">
                <span className="block">
                  <RevealText text="Every store." />
                </span>
                <span className="block">
                  <RevealText text="One" delay={0.2} />{" "}
                  <RevealText
                    text="search."
                    delay={0.28}
                    className="font-serif font-normal italic tracking-[-0.025em]"
                  />
                </span>
              </h1>
              <div className="relative mt-10 flex items-end justify-between gap-8 lg:max-w-[52%]">
                <motion.p
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7, duration: 1, ease: EASE }}
                  className="max-w-md text-[15px] leading-relaxed text-ash"
                >
                  Live prices from Amazon, Flipkart, Myntra and AJIO — de-duplicated, sorted and compared in one place,
                  with your card&rsquo;s offers already applied.
                </motion.p>
                <motion.div
                  initial={{ opacity: 0, scale: 0.6, rotate: -40 }}
                  animate={{ opacity: 1, scale: 1, rotate: 0 }}
                  transition={{ delay: 0.8, duration: 1.2, ease: EASE }}
                  className="hidden sm:block lg:hidden"
                >
                  <SpinBadge text="One search · Every store · " />
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence initial={false}>
          {hasSearched && (
            <motion.div
              key="back-row"
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.6, ease: EASE, delay: 0.2 }}
              className="mb-8 flex items-center gap-5"
            >
              <Magnetic strength={0.25}>
                <button
                  type="button"
                  onClick={onBack}
                  data-cursor="Back"
                  className="group flex h-11 items-center gap-2 rounded-full border border-ink pl-3.5 pr-5 text-[13px] font-medium transition-colors duration-300 hover:bg-ink hover:text-paper"
                >
                  <ArrowRight className="h-4 w-4 rotate-180 transition-transform duration-500 ease-expo group-hover:-translate-x-1" />
                  <RollText>Back</RollText>
                </button>
              </Magnetic>
              <nav
                aria-label="Breadcrumb"
                className="flex min-w-0 items-center gap-2 font-mono text-[11px] uppercase tracking-[0.16em] text-ash"
              >
                <button
                  type="button"
                  onClick={() => onNavigate(null, 1)}
                  className="flex shrink-0 items-center gap-1.5 transition-colors hover:text-ink"
                >
                  <HomeIcon className="h-3.5 w-3.5" />
                  Home
                </button>
                <span aria-hidden>/</span>
                <span className="truncate text-ink" aria-current={routePage === 1 ? "page" : undefined}>
                  {routeQuery}
                </span>
                {routePage > 1 && (
                  <>
                    <span aria-hidden>/</span>
                    <span className="shrink-0 text-ink" aria-current="page">
                      Page {routePage}
                    </span>
                  </>
                )}
              </nav>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: hasSearched ? 0 : 0.55, duration: 1, ease: EASE }}
          className="group/search relative flex items-center gap-4 border-b border-ink/15 pb-4"
        >
          <SearchIcon className="h-6 w-6 shrink-0 text-ash sm:h-8 sm:w-8" />
          <div className="relative min-w-0 flex-1">
            <input
              type="text"
              aria-label="Search products"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full bg-transparent text-2xl tracking-[-0.03em] outline-none sm:text-[2.6rem]"
            />
            {!query && (
              <div
                aria-hidden
                className="pointer-events-none absolute inset-0 flex items-center overflow-hidden text-2xl tracking-[-0.03em] text-ash/60 sm:text-[2.6rem]"
              >
                <AnimatePresence initial={false}>
                  <motion.span
                    key={suggestionIndex}
                    initial={{ y: "100%", opacity: 0 }}
                    animate={{ y: "0%", opacity: 1 }}
                    exit={{ y: "-100%", opacity: 0 }}
                    transition={{ duration: 0.7, ease: EASE }}
                    className="absolute inset-x-0 truncate"
                  >
                    {SUGGESTIONS[suggestionIndex]}
                  </motion.span>
                </AnimatePresence>
              </div>
            )}
          </div>
          <Magnetic>
            <button
              type="submit"
              aria-label="Search"
              data-cursor="Search"
              className="group/btn flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-ink text-paper transition-colors duration-500 hover:bg-acid hover:text-ink sm:h-[4.5rem] sm:w-[4.5rem]"
            >
              <ArrowRight className="h-5 w-5 transition-transform duration-500 ease-expo group-hover/btn:-rotate-45 sm:h-6 sm:w-6" />
            </button>
          </Magnetic>
          <span
            aria-hidden
            className="absolute -bottom-px left-0 h-[2px] w-full origin-left scale-x-0 bg-ink transition-transform duration-700 ease-expo group-focus-within/search:scale-x-100"
          />
        </motion.form>

        {!hasSearched && (
          <motion.div
            initial="hidden"
            animate="show"
            variants={{ show: { transition: { staggerChildren: 0.06, delayChildren: 0.9 } } }}
            className="mt-6 flex flex-wrap items-center gap-2"
          >
            <span className={`mr-2 ${eyebrow}`}>Try</span>
            {SUGGESTIONS.slice(0, 4).map((s) => (
              <motion.button
                key={s}
                type="button"
                onClick={() => searchFor(s)}
                variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: EASE } } }}
                className="rounded-full border border-line px-4 py-2 text-[13px] transition-colors duration-300 hover:border-ink hover:bg-ink hover:text-paper"
              >
                {s}
              </motion.button>
            ))}
          </motion.div>
        )}
      </section>

      {!hasSearched && (
        <>
          <div aria-hidden className="relative my-24 sm:my-32">
            <Marquee
              duration={38}
              className="relative z-10 -mx-[5vw] -rotate-2 bg-ink py-5 text-paper sm:py-7"
              items={MARKETPLACES.map((name, i) => (
                <span key={name} className="flex items-center">
                  <span
                    className={
                      i % 2
                        ? "px-8 font-serif text-5xl italic text-acid sm:text-7xl"
                        : "px-8 text-4xl font-semibold uppercase tracking-[-0.04em] sm:text-6xl"
                    }
                  >
                    {name}
                  </span>
                  <span className="text-2xl text-acid sm:text-3xl">✦</span>
                </span>
              ))}
            />
            <Marquee
              duration={44}
              reverse
              className="relative -mx-[5vw] -mt-6 rotate-[1.5deg] bg-acid py-3 text-ink sm:-mt-8 sm:py-4"
              items={["Compare", "Save", "Search once", "Card offers"].map((word) => (
                <span key={word} className="flex items-center font-mono text-sm uppercase tracking-[0.2em] sm:text-base">
                  <span className="px-6">{word}</span>
                  <span>—</span>
                </span>
              ))}
            />
          </div>

          <HowItWorks />
          <div className="h-24 sm:h-40" />
          <CategoryIndex onSelect={searchFor} />
        </>
      )}

      {hasSearched && (
        <section className="mx-auto max-w-[1400px] px-4 pb-8 pt-12 sm:px-8">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="min-w-0">
              <p className={eyebrow}>
                Results
                {result?.cache_hit && <span className="ml-3 rounded-full bg-bone px-2 py-0.5">Cached</span>}
              </p>
              <h2 className="mt-3 text-4xl font-medium leading-[0.95] tracking-[-0.05em] sm:text-6xl">
                {result ? (
                  <>
                    <AnimatedNumber value={result.total} />{" "}
                    <span className="font-serif font-normal italic tracking-[-0.02em]">for</span>{" "}
                    <span className="break-words">&ldquo;{result.query}&rdquo;</span>
                  </>
                ) : (
                  <span className="text-ash">Searching…</span>
                )}
              </h2>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <select
                  value={cardId}
                  onChange={(e) => handleCardChange(e.target.value)}
                  aria-label="Bank card"
                  className="h-10 appearance-none rounded-full border border-line bg-transparent pl-4 pr-10 text-[13px] font-medium outline-none transition-colors hover:border-ink focus:border-ink"
                >
                  <option value="">No card</option>
                  {cards.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.bank_name} {c.card_name}
                    </option>
                  ))}
                </select>
                <ChevronDown className="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2" />
              </div>
              <button
                type="button"
                onClick={() => setShowAddCard((v) => !v)}
                aria-expanded={showAddCard}
                className="flex h-10 items-center gap-1.5 rounded-full border border-line px-4 text-[13px] font-medium transition-colors hover:border-ink"
              >
                <PlusIcon className={`h-4 w-4 transition-transform duration-500 ease-expo ${showAddCard ? "rotate-45" : ""}`} />
                Card
              </button>
              <LiveFiltersPopup filters={filters} onApply={handleFiltersApply} />
            </div>
          </div>

          <AnimatePresence initial={false}>
            {showAddCard && (
              <motion.form
                onSubmit={handleAddCard}
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.6, ease: EASE }}
                className="overflow-hidden"
              >
                <div className="mt-8 grid items-end gap-6 rounded-[6px] bg-bone p-6 sm:grid-cols-[1fr_1fr_auto]">
                  <Field
                    label="Bank, e.g. HDFC"
                    value={newCard.bank_name}
                    onChange={(e) => setNewCard((f) => ({ ...f, bank_name: e.target.value }))}
                  />
                  <Field
                    label="Card, e.g. Regalia"
                    value={newCard.card_name}
                    onChange={(e) => setNewCard((f) => ({ ...f, card_name: e.target.value }))}
                  />
                  <button
                    type="submit"
                    className="group h-12 rounded-full bg-ink px-8 text-[14px] font-medium text-paper transition-colors duration-500 hover:bg-acid hover:text-ink"
                  >
                    <RollText>Add card</RollText>
                  </button>
                  <p className="text-xs leading-relaxed text-ash sm:col-span-3">
                    Offers for a card are added via the API (<code className="font-mono">POST /cards/{"{card_id}"}/offers</code>)
                    — until a card has offers, no discount will show for it.
                  </p>
                </div>
              </motion.form>
            )}
          </AnimatePresence>

          <div className="mt-8 flex items-center justify-between gap-6 border-y border-line">
          <div className="no-scrollbar -mx-4 min-w-0 flex-1 overflow-x-auto px-4 py-3 sm:mx-0 sm:px-0">
            <div className="flex w-max items-center gap-1">
              <span className={`mr-3 ${eyebrow}`}>Sort</span>
              {LIVE_SORT_OPTIONS.map((o) => (
                <button
                  key={o.value}
                  onClick={() => handleSortChange(o.value)}
                  aria-pressed={sort === o.value}
                  className="relative rounded-full px-4 py-2 text-[13px] font-medium"
                >
                  {sort === o.value && (
                    <motion.span
                      layoutId="sort-pill"
                      className="absolute inset-0 rounded-full bg-ink"
                      transition={{ type: "spring", stiffness: 420, damping: 34 }}
                    />
                  )}
                  <span className={`relative transition-colors duration-300 ${sort === o.value ? "text-paper" : "text-ash hover:text-ink"}`}>
                    {o.label}
                  </span>
                </button>
              ))}
            </div>
          </div>
          <div className="hidden shrink-0 items-center gap-1 md:flex" role="group" aria-label="Grid density">
            {([2, 3, 4] as Density[]).map((n) => (
              <button
                key={n}
                onClick={() => setDensity(n)}
                aria-pressed={density === n}
                aria-label={`${n} columns`}
                className={`relative flex h-9 w-9 items-center justify-center rounded-full ${n === 4 ? "hidden xl:flex" : ""}`}
              >
                {density === n && (
                  <motion.span
                    layoutId="density-pill"
                    className="absolute inset-0 rounded-full bg-ink"
                    transition={{ type: "spring", stiffness: 420, damping: 34 }}
                  />
                )}
                <span
                  className={`relative grid gap-[2px] ${density === n ? "text-paper" : "text-ash"}`}
                  style={{ gridTemplateColumns: `repeat(${n}, 3px)` }}
                >
                  {Array.from({ length: n * 2 }).map((_, i) => (
                    <span key={i} className="h-[5px] rounded-[1px] bg-current" />
                  ))}
                </span>
              </button>
            ))}
          </div>
          </div>

          {noProvidersEnabled && (
            <Notice label="Setup">
              No live data providers are enabled — set <code className="font-mono">SERPAPI_API_KEY</code> in the
              backend&rsquo;s <code className="font-mono">.env</code> to get real results.
            </Notice>
          )}
          {unavailableProviders.length > 0 && (
            <Notice label="Partial">
              {unavailableProviders.map(([name]) => name).join(", ")} unavailable for this search — showing results
              from other providers.
            </Notice>
          )}
          {error && (
            <Notice label="Error" tone="error">
              {error}
            </Notice>
          )}

          <div className="mt-12">
            {loading ? (
              <div className={`grid grid-cols-2 gap-x-4 gap-y-12 xl:gap-x-6 ${DENSITY_CLASSES[density]}`}>
                {Array.from({ length: 8 }).map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : !error && result && result.results.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: EASE }}
                className="py-24 text-center"
              >
                <p className="font-serif text-5xl italic tracking-[-0.02em] sm:text-7xl">Nothing yet.</p>
                <p className="mt-4 text-[15px] text-ash">No products matched. Try a different search or loosen the filters.</p>
              </motion.div>
            ) : (
              !error &&
              result && (
                <>
                  <div className={`grid grid-cols-2 gap-x-4 gap-y-12 xl:gap-x-6 ${DENSITY_CLASSES[density]}`}>
                    {result.results.map((p, i) => (
                      <LiveProductCard key={`${result.page}-${p.id}`} product={p} index={i} />
                    ))}
                  </div>
                  <Pagination page={page} pageSize={result.limit} total={result.total} onChange={handlePageChange} />
                </>
              )
            )}
          </div>
        </section>
      )}
    </div>
  );
}

function Notice({
  label,
  tone = "info",
  children,
}: {
  label: string;
  tone?: "info" | "error";
  children: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: EASE }}
      className={`mt-6 flex gap-4 border-l-2 py-1 pl-4 text-sm leading-relaxed ${tone === "error" ? "border-ember text-ember" : "border-ink text-ink/80"}`}
    >
      <span className="shrink-0 pt-0.5 font-mono text-[10px] uppercase tracking-[0.18em] text-ash">{label}</span>
      <span>{children}</span>
    </motion.div>
  );
}

function SkeletonCard() {
  return (
    <div>
      <div className="relative aspect-[4/5] overflow-hidden rounded-[6px] bg-bone">
        <div className="absolute inset-0 animate-shimmer bg-linear-to-r from-transparent via-paper/70 to-transparent" />
      </div>
      <div className="mt-4 h-2.5 w-1/3 rounded-full bg-bone" />
      <div className="mt-2.5 h-3.5 w-4/5 rounded-full bg-bone" />
      <div className="mt-4 h-5 w-1/4 rounded-full bg-bone" />
    </div>
  );
}
