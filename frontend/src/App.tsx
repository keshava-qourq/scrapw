import { useState } from "react";
import WatchlistView from "./components/WatchlistView";
import LiveSearchView from "./components/LiveSearchView";

export default function App() {
  const [tab, setTab] = useState<"live" | "compare">("live");

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3h1.5l1.5 12.75h11.25M6.75 15.75L8.25 6h11.63l-1.4 9.75M9 20.25a.75.75 0 100-1.5.75.75 0 000 1.5zM18 20.25a.75.75 0 100-1.5.75.75 0 000 1.5z" />
              </svg>
            </div>
            <span className="text-lg font-semibold tracking-tight text-slate-900">ScrapW Search</span>
            <div className="ml-4 flex gap-1 rounded-lg bg-slate-100 p-1">
              <button
                onClick={() => setTab("live")}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  tab === "live" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
                }`}
              >
                Live search
              </button>
              <button
                onClick={() => setTab("compare")}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  tab === "compare" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
                }`}
              >
                Compare prices
              </button>
            </div>
          </div>
        </div>
      </header>

      {tab === "compare" ? <WatchlistView /> : <LiveSearchView />}
    </div>
  );
}
