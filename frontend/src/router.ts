import { useCallback, useEffect, useState } from "react";

/**
 * Minimal URL-backed navigation, so searches get real history entries:
 *   /                 home (search landing)
 *   /?q=shoes&page=2  search results
 *   /?view=board      price board
 */
export type View = "live" | "compare";

export interface Route {
  view: View;
  q: string | null;
  page: number;
}

export const HOME: Route = { view: "live", q: null, page: 1 };

const DEPTH_KEY = "scrapwDepth";

function readRoute(): Route {
  const params = new URLSearchParams(window.location.search);
  if (params.get("view") === "board") return { view: "compare", q: null, page: 1 };
  const q = params.get("q")?.trim() || null;
  const page = Math.max(1, Math.floor(Number(params.get("page"))) || 1);
  return { view: "live", q, page: q ? page : 1 };
}

function toUrl(route: Route): string {
  const params = new URLSearchParams();
  if (route.view === "compare") params.set("view", "board");
  else if (route.q) {
    params.set("q", route.q);
    if (route.page > 1) params.set("page", String(route.page));
  }
  const search = params.toString();
  return search ? `?${search}` : window.location.pathname;
}

/** How many entries deep into this app's own history we are (0 = first page loaded). */
function currentDepth(): number {
  const depth = (window.history.state as Record<string, unknown> | null)?.[DEPTH_KEY];
  return typeof depth === "number" ? depth : 0;
}

export function useRoute() {
  const [route, setRoute] = useState<Route>(readRoute);

  useEffect(() => {
    const handlePop = () => setRoute(readRoute());
    window.addEventListener("popstate", handlePop);
    return () => window.removeEventListener("popstate", handlePop);
  }, []);

  const navigate = useCallback((next: Route, options: { replace?: boolean } = {}) => {
    const url = toUrl(next);
    const unchanged = url === toUrl(readRoute());
    if (options.replace || unchanged) {
      window.history.replaceState({ [DEPTH_KEY]: currentDepth() }, "", url);
    } else {
      window.history.pushState({ [DEPTH_KEY]: currentDepth() + 1 }, "", url);
    }
    setRoute(next);
  }, []);

  /** Step back through in-app history; if there's nothing to go back to, go home. */
  const goBack = useCallback(() => {
    if (currentDepth() > 0) window.history.back();
    else navigate(HOME);
  }, [navigate]);

  return { route, navigate, goBack };
}
