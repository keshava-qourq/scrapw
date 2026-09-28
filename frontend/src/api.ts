import type {
  AuthResponse,
  Card,
  CardCreate,
  LiveMarketplace,
  LiveSearchResponse,
  LiveSortOption,
  User,
  WatchlistGroup,
  WatchlistItem,
  WatchlistItemCreate,
} from "./types";

const TOKEN_KEY = "scrapw.accessToken";

/** Fired when the backend rejects our token, so the app can drop back to the login screen. */
export const AUTH_EXPIRED_EVENT = "scrapw:auth-expired";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Storage unavailable (e.g. private mode) — the session just won't survive a reload.
  }
}

async function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(input, { ...init, headers });
  if (res.status === 401 && token) {
    setToken(null);
    window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
  }
  return res;
}

async function authRequest(path: "login" | "register", email: string, password: string): Promise<User> {
  const res = await fetch(`/api/v1/auth/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    // 422s carry a list of field errors; surface the first one's message.
    const detail = Array.isArray(body.detail) ? body.detail[0]?.msg : body.detail;
    throw new Error(detail ?? `Request failed (${res.status})`);
  }
  const data: AuthResponse = await res.json();
  setToken(data.access_token);
  return data.user;
}

export function login(email: string, password: string): Promise<User> {
  return authRequest("login", email, password);
}

export function register(email: string, password: string): Promise<User> {
  return authRequest("register", email, password);
}

export async function getCurrentUser(): Promise<User | null> {
  if (!getToken()) return null;
  const res = await apiFetch("/api/v1/auth/me");
  if (res.status === 401) return null;
  if (!res.ok) throw new Error(`Failed to load account (${res.status})`);
  return res.json();
}

export function logout(): void {
  setToken(null);
}

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

  const res = await apiFetch(`/api/v1/search/live?${query.toString()}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Live search failed (${res.status})`);
  }
  return res.json();
}

export async function listCards(): Promise<Card[]> {
  const res = await apiFetch("/api/v1/cards");
  if (!res.ok) throw new Error(`Failed to load cards (${res.status})`);
  return res.json();
}

export async function createCard(card: CardCreate): Promise<Card> {
  const res = await apiFetch("/api/v1/cards", {
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
  const res = await apiFetch("/api/v1/watchlist", {
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
  const res = await apiFetch("/api/v1/watchlist/groups");
  if (!res.ok) throw new Error(`Failed to load watchlist (${res.status})`);
  return res.json();
}

export async function deleteWatchlistItem(id: string): Promise<void> {
  const res = await apiFetch(`/api/v1/watchlist/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204) throw new Error(`Failed to delete item (${res.status})`);
}
