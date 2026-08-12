import type {
  Card,
  CardCreate,
  LiveMarketplace,
  LiveSearchResponse,
  LiveSortOption,
  WatchlistGroup,
  WatchlistItem,
  WatchlistItemCreate,
} from "./types";

export interface LiveSearchParams {
  q: string;
  page: number;
  limit: number;
  marketplace?: LiveMarketplace;
  min_price?: number;
  max_price?: number;
  min_rating?: number;
  sort: LiveSortOption;
  card_id?: string;
}

export async function searchLive(params: LiveSearchParams): Promise<LiveSearchResponse> {
  const query = new URLSearchParams({
    q: params.q,
    page: String(params.page),
    limit: String(params.limit),
    sort: params.sort,
  });
  if (params.marketplace) query.set("marketplace", params.marketplace);
  if (params.min_price != null) query.set("min_price", String(params.min_price));
  if (params.max_price != null) query.set("max_price", String(params.max_price));
  if (params.min_rating != null) query.set("min_rating", String(params.min_rating));
  if (params.card_id) query.set("card_id", params.card_id);

  const res = await fetch(`/api/v1/search/live?${query.toString()}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Live search failed (${res.status})`);
  }
  return res.json();
}

export async function listCards(): Promise<Card[]> {
  const res = await fetch("/api/v1/cards");
  if (!res.ok) throw new Error(`Failed to load cards (${res.status})`);
  return res.json();
}

export async function createCard(card: CardCreate): Promise<Card> {
  const res = await fetch("/api/v1/cards", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(card),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Failed to add card (${res.status})`);
  }
  return res.json();
}

export async function addWatchlistItem(item: WatchlistItemCreate): Promise<WatchlistItem> {
  const res = await fetch("/api/v1/watchlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Failed to add item (${res.status})`);
  }
  return res.json();
}

export async function listWatchlistGroups(): Promise<WatchlistGroup[]> {
  const res = await fetch("/api/v1/watchlist/groups");
  if (!res.ok) throw new Error(`Failed to load watchlist (${res.status})`);
  return res.json();
}

export async function deleteWatchlistItem(id: string): Promise<void> {
  const res = await fetch(`/api/v1/watchlist/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204) throw new Error(`Failed to delete item (${res.status})`);
}
