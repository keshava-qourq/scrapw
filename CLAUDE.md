# CLAUDE.md

Guidance for working in this repo.

## What this is

Async multi-marketplace product search engine (Amazon, Flipkart, AJIO, Myntra). See
[README.md](README.md) for architecture, setup, and API docs — read it first.

The repo has two top-level parts:
- `backend/` — the FastAPI + Celery service described below.
- `frontend/` — a React/Vite UI that talks to the backend's HTTP API only.

## Hard rules

- **User search never waits on a marketplace.** `GET /products/search` reads only from
  OpenSearch (`backend/app/services/search_service.py`). Ingestion (`backend/app/workers/`) is
  fully separate and asynchronous. Never make an API route call a connector directly.
- **No marketplace-specific code outside `backend/app/connectors/<marketplace>/`.** Services,
  API routes, and workers only ever touch `MarketplaceConnector` (the interface) or
  `backend/app/connectors/registry.py` (the factory).
- **Never bypass CAPTCHA, auth, bot detection, robots rules, or rate limits.** If a marketplace
  has no official API/affiliate feed, the connector stays mock-only (clearly labeled fixture
  data) — see the AJIO/Myntra connectors for the pattern. Do not fabricate data and present it
  as if it came from a real marketplace.
- **Every connector respects its own conservative rate limit** (`ConnectorConfig` /
  `RateLimiter`). Don't raise the defaults without a documented reason (e.g. a published API
  quota).
- **A failure in one marketplace's ingestion job must not affect another's.** Celery tasks are
  per-marketplace and retry with capped exponential backoff; they log and stop, never crash the
  scheduler or another marketplace's task.
- **Never hardcode credentials.** All config comes from `backend/app/core/config.py` /
  environment variables; `backend/.env` is gitignored, `backend/.env.example` has placeholders
  only.

## Before committing changes

```bash
cd backend
source .venv/bin/activate
pytest
```

Tests must not require a real database, Redis, OpenSearch, or marketplace network access —
use dependency overrides / fakes (see `backend/tests/integration/test_products_search_api.py`)
or the mock catalogs already in each connector.

## Common tasks

- **Add a marketplace** — see README's "Adding a new marketplace" section.
- **Add a search filter/sort option** — extend `backend/app/schemas/search.py`, then
  `backend/app/search/opensearch.py::_SORT_MAP` / the filter-building loop in `search()`, then
  the query params in `backend/app/api/v1/products.py::search_products`.
- **Add a DB column** — edit the model in `backend/app/models/`, then write an Alembic migration
  by hand under `backend/app/db/migrations/versions/` (the sandbox this was built in has no
  network access for `alembic revision --autogenerate` against a scratch DB, but that command
  works fine locally if you have Postgres running — prefer it over hand-writing when you can).
- **Add a future feature stub** (offers, price history, etc.) — add the schema to
  `backend/app/schemas/`, wire a route that returns an empty/placeholder response, and note it
  under "What's deliberately not built yet" in the README, rather than half-implementing it.
