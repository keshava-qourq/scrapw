# Product Search Engine

An async, multi-marketplace product search and comparison API (Amazon, Flipkart, AJIO, Myntra).
User search reads from OpenSearch and returns instantly; marketplace ingestion happens entirely
in the background via Celery workers and never blocks a request.

```
User → FastAPI → SearchService → OpenSearch → indexed products (fast, synchronous)

Scheduler (celery-beat) → refresh_marketplace → fetch_marketplace_products
    → per-marketplace connector → normalize → deduplicate → PostgreSQL → index_products → OpenSearch
```

## Stack

FastAPI · SQLAlchemy (async) · Alembic · PostgreSQL · OpenSearch · Redis · Celery · httpx

## Project layout

```
backend/
  app/
    api/v1/          product/marketplace/category/health/watchlist/live-search routes
    ai/               GeminiClient (shared) + GeminiQueryProcessor (NL query -> ParsedQuery)
    core/             config, logging, exceptions, rate limiter
    models/           SQLAlchemy models (Product, Marketplace, CanonicalProduct, WatchlistItem, SearchHistory)
    schemas/          Pydantic request/response models (incl. live_search.py)
    services/         product, search, query-understanding, watchlist, live-search orchestration,
                      normalization, dedup services
    providers/        ProductSearchProvider interface + SerpApiProductSearchProvider
    cache/            SearchCache interface + Redis implementation (live-search caching)
    repositories/      DB access, isolated from services
    connectors/        one package per marketplace, behind a common interface (mock ingestion pipeline)
    search/            SearchIndex interface + OpenSearch implementation
    workers/            celery app, ingestion tasks, indexing tasks
    db/                 engine/session + Alembic migrations
  tests/
    unit/               normalization, dedup signature, search service, watchlist, query understanding,
                        marketplace detection, SerpApi provider, live-search service, live-search cache
    connectors/         per-marketplace connector tests (mock data, no network)
    integration/        FastAPI endpoint tests
frontend/
  src/
    components/        SearchBar, FiltersSidebar, ProductCard, Pagination, WatchlistView
    api.ts, types.ts    typed client for the backend HTTP API
```

## Getting started

### Docker (recommended)

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

This starts Postgres, Redis, OpenSearch, the API (`:8000`), a Celery worker, and Celery beat.
`alembic upgrade head` runs automatically before the API starts. (The frontend isn't
containerized yet — run it separately per below.)

### Local development

Requires Python 3.12+, a running PostgreSQL and (optionally) Redis/OpenSearch.

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL etc. to match your local services
alembic upgrade head
uvicorn app.main:app --reload
```

Run a worker + beat locally (needs Redis):

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

Run the frontend (needs the backend API reachable at `:8001`, or edit the proxy target in
`frontend/vite.config.ts`):

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
cd backend
pytest
```

Tests never hit a real marketplace, database, or search cluster — connector tests exercise
the mock catalogs, and API tests use FastAPI dependency overrides with fakes.

## API

| Endpoint | Description |
|---|---|
| `GET /api/v1/health` | Liveness check |
| `GET /api/v1/products/search` | Search indexed products (query, filters, sort, pagination) |
| `GET /api/v1/products/search/smart` | Same, but filters are derived from a natural-language query via Gemini (`GEMINI_API_KEY`); falls back to a plain-text search if unset or unavailable |
| `GET /api/v1/search/live` | **Real** cross-marketplace results via SerpApi (see below) — not the mock/ingested pipeline the other endpoints use |
| `GET /api/v1/products/{id}` | Fetch one product from PostgreSQL |
| `GET /api/v1/products/{id}/offers` | Placeholder for future bank/card offers, coupons, cashback (returns `[]` today) |
| `GET /api/v1/marketplaces` | List configured marketplaces |
| `GET /api/v1/categories` | Distinct product categories seen so far |
| `POST /api/v1/watchlist` | Log a price you found by hand for a product on some marketplace |
| `GET /api/v1/watchlist/groups` | All logged prices grouped by product name, sorted cheapest-first, with lowest-price/highest-rated flagged |
| `DELETE /api/v1/watchlist/{id}` | Remove a logged price |

`GET /api/v1/products/search` filters: `marketplace`, `brand`, `category`, `min_price`,
`max_price`, `min_rating`, `min_discount`, `availability`, `size`, `color`.
Sort: `relevance` (default), `price_low_to_high`, `price_high_to_low`, `rating`, `discount`, `newest`.

The watchlist is a manually-curated price board, not a live feed — see "What's deliberately
not built yet" below for why this project can't automatically scrape live prices across
marketplaces.

## Marketplace connectors

Every marketplace implements `app.connectors.base.MarketplaceConnector`:

```python
class MarketplaceConnector(ABC):
    async def search_products(self, query, **kwargs) -> list[RawProduct]: ...
    async def fetch_product(self, url) -> RawProduct | None: ...
    async def fetch_product_details(self, product_id) -> RawProduct | None: ...
    def normalize_product(self, raw_product) -> dict: ...
```

No other part of the app imports a marketplace-specific module — `backend/app/connectors/registry.py`
is the only place that maps a marketplace code to a connector class.

**Current state, per marketplace** (see each connector's docstring for detail):

| Marketplace | Real access path | Status |
|---|---|---|
| Amazon | Product Advertising API (PA-API 5.0), for approved Associates | Structured, not yet implemented (`NotImplementedError` with a link to PA-API docs); serves mock data by default |
| Flipkart | Affiliate API, after approval at affiliate.flipkart.com | Structured, not yet implemented; serves mock data by default |
| AJIO | No publicly documented affiliate/API access found | Mock-only until a permitted access mechanism exists |
| Myntra | No publicly documented affiliate/API access found | Mock-only until a permitted access mechanism exists |

No connector scrapes a marketplace directly, bypasses CAPTCHA/auth/bot-detection, or fabricates
data pretending to be real. The mock catalogs are clearly labeled ("(Mock Listing)") and exist
only so the rest of the pipeline (normalization → dedup → indexing → search) can be exercised
end-to-end without credentials.

To enable a real connector: set `<MARKETPLACE>_API_ENABLED=true` and the relevant
`<MARKETPLACE>_API_KEY` / `_API_SECRET` in `backend/.env`, then implement the `TODO` in that
connector's `connector.py` (the parser/mapper are already written against each API's
documented response shape).

### Adding a new marketplace

1. Create `backend/app/connectors/<marketplace>/{connector.py,parser.py,mapper.py}`.
2. Implement `MarketplaceConnector`; `mapper.py` must return a dict matching
   `backend/app/schemas/product.py::ProductCreate` field names (see any existing mapper).
3. Register the class in `backend/app/connectors/registry.py`.
4. Add `<MARKETPLACE>_*` settings to `backend/app/core/config.py` and `backend/.env.example`.
5. Add it to `SUPPORTED_MARKETPLACES` (automatic via the registry) so celery-beat
   schedules a `refresh_marketplace` job for it.
6. Add connector tests under `backend/tests/connectors/`, mocking all network access.

## Background workers

- `celery-beat` schedules one `refresh_marketplace(code)` job per marketplace, staggered
  15 minutes apart so they don't compete for the same rate-limit budget.
- `refresh_marketplace` fans out `fetch_marketplace_products(code, query)` per seed query.
- `fetch_marketplace_products` runs fetch → normalize → validate → store → dedup →
  (async) `index_products`, for one marketplace only. A failure in one marketplace's task
  (timeout, validation error) retries with exponential backoff and, once exhausted, is logged
  and swallowed — it never affects another marketplace's jobs.
- `index_products` is a separate task, decoupled from ingestion, so search-index outages don't
  block writes to PostgreSQL and vice versa.
- `update_product` / `deduplicate_products` / `normalize_product` are standalone tasks for
  targeted refreshes and reprocessing.

Every connector has its own `requests_per_second` / `max_concurrent_requests` /
`timeout_seconds` / `retry_count`, enforced by a shared token-bucket `RateLimiter`
(`backend/app/connectors/rate_limiter.py`). Defaults are conservative (1 req/s, 2 concurrent).

## Live search (`GET /api/v1/search/live`)

The endpoints above (`/products/search`, `/products/search/smart`) read from a pre-ingested
OpenSearch index populated by the mock/connector pipeline. `/search/live` is a separate,
independent path that returns **real** results, right now, across Amazon, Flipkart, Myntra, and
AJIO — without needing Amazon/Flipkart affiliate approval or touching AJIO/Myntra directly
(neither has a public API, and this project won't scrape either — see Hard rules in `CLAUDE.md`).

It does this by calling **SerpApi**'s `google_shopping` engine, a licensed data aggregator that
handles marketplace access under its own agreements. This project never scrapes a marketplace
itself for this endpoint.

### Flow

```
GET /api/v1/search/live?q=...
        ↓
check Redis cache (query + filters hash) → hit? return cached response
        ↓ (miss)
GeminiQueryProcessor.parse(q)            # natural language → ParsedQuery (keywords/brand/category/price)
        ↓                                 # falls back to naive keyword split if Gemini is unset/fails
asyncio.gather(*enabled providers)       # MVP: just SerpApiProductSearchProvider, bounded by
        ↓                                 # MAX_CONCURRENT_PROVIDERS; one provider failing never
        ↓                                 # fails the others — see `marketplace_status` in the response
ProductNormalizer                        # provider payload → common LiveProduct schema, nothing fabricated
        ↓
deduplicate_live_products                # groups same product across marketplaces, confidence score
        ↓
filter (marketplace/price/rating) → sort → paginate
        ↓
cache response in Redis (SEARCH_CACHE_TTL_SECONDS, default 15 min)
        ↓
record row in `search_history` (query, filters, result count — no user identity)
```

### Setup

1. Get a free SerpApi key at [serpapi.com](https://serpapi.com) (free tier: ~100 searches/month).
2. Set `SERPAPI_API_KEY` in `backend/.env`. Until it's set, `/search/live` returns
   `"marketplace_status": {}` and zero results rather than erroring — the endpoint degrades to
   "no providers enabled," not a crash.
3. Gemini query understanding reuses the existing `GEMINI_API_KEY` (see `/products/search/smart`
   above); also optional — the endpoint falls back to naive keyword extraction if unset.

### Adding another provider later

Implement `app.providers.base.ProductSearchProvider` (`async search(query, limit) -> list[LiveProduct]`),
register it in `get_live_search_providers` (`backend/app/api/deps.py`). `LiveSearchService` only
ever depends on the `ProductSearchProvider` interface, so this never requires touching orchestration,
dedup, filtering, or sorting code. A direct marketplace API provider (Amazon PA-API, Flipkart
Affiliate API) would slot in the same way, once/if you have approved credentials for one.

### Known MVP limitations

- `total` in the response reflects the pool of results actually fetched this call (bounded per
  provider), not a true marketplace-wide count — no provider exposes one, so deep pagination is
  approximate. This matches how Google Shopping itself behaves, not a bug here.
- Deduplication uses the same conservative normalized-signature matching as the ingested
  pipeline (`build_match_signature`) — deliberately simple, and it will miss looser duplicates
  (different phrasing, model numbers) rather than risk merging unrelated products.
- Search history is written best-effort; a DB write failure is logged and swallowed, never fails
  the search response.

## Environment variables

See `backend/.env.example` for the full list (database, Redis, OpenSearch, Gemini, SerpApi, and
per-marketplace credentials/rate limits). Never commit a real `backend/.env`.

## Deduplication

`backend/app/services/deduplication_service.py` groups products from different marketplaces under a
shared `CanonicalProduct` using a normalized (brand + name) signature — lowercased, punctuation
stripped, filler words (`men`, `women`, `unisex`, ...) removed, tokens sorted. This is
intentionally simple; `DeduplicationService.find_canonical_match` is the single seam to replace
with fuzzy/embedding-based matching later without touching ingestion callers.

## What's deliberately not built yet

Architecture supports these but they are not implemented (see `backend/app/schemas/offer.py` and
`GET /products/{id}/offers` for the extension point):

- Bank/card offers, coupons, cashback, EMI, exchange offers, effective-price calculation
- Semantic/embedding-based search and product matching
- Automated live price scraping/aggregation across marketplaces. Amazon and Flipkart only
  expose product data through affiliate programs gated on approval (and, for Amazon PA-API,
  ongoing qualifying sales); AJIO and Myntra have no public product API at all. Bypassing that
  via scraping would mean evading bot detection and breaking those sites' terms of service,
  which this project won't do (see Hard rules in `CLAUDE.md`). The `/watchlist` endpoints are
  the practical alternative: a manually-curated price board instead of an automated feed.
