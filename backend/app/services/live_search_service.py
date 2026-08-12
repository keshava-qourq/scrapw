import asyncio

from app.ai.query_processor import GeminiQueryProcessor
from app.cache.search_cache import SearchCache, build_cache_key
from app.core.logging import get_logger
from app.providers.base import ProductSearchProvider, ProviderUnavailableError
from app.schemas.live_search import LiveProduct, LiveSearchFilters, LiveSearchResponse, LiveSortOption
from app.services.live_deduplication_service import deduplicate_live_products

logger = get_logger(__name__)

_SORT_KEYS = {
    LiveSortOption.PRICE_LOW_TO_HIGH: lambda p: (p.price is None, p.price or 0),
    LiveSortOption.PRICE_HIGH_TO_LOW: lambda p: (p.price is None, -(p.price or 0)),
    LiveSortOption.RATING: lambda p: (p.rating is None, -(p.rating or 0)),
    LiveSortOption.DISCOUNT: lambda p: (p.discount_percentage is None, -(p.discount_percentage or 0)),
}


class LiveSearchService:
    """
    Orchestrates a live cross-marketplace search: Gemini query understanding
    -> query every provider concurrently (bounded, one failure never fails
    the others) -> dedupe -> filter -> sort -> paginate. Callers only ever
    depend on `ProductSearchProvider`, never a concrete provider — adding
    another data source later is a registration, not a rewrite here.

    `total` in the response reflects the pool of results actually fetched
    from providers this call (bounded by `fetch_limit` below), not a true
    marketplace-wide count — providers don't expose one, so deep pagination
    is inherently approximate. This matches SerpApi/Google Shopping's own
    behavior, not a bug in this service.
    """

    def __init__(
        self,
        providers: list[ProductSearchProvider],
        query_processor: GeminiQueryProcessor,
        max_concurrent_providers: int = 4,
        cache: SearchCache | None = None,
        cache_ttl_seconds: int = 900,
    ):
        self._providers = providers
        self._query_processor = query_processor
        self._semaphore = asyncio.Semaphore(max_concurrent_providers)
        self._cache = cache
        self._cache_ttl_seconds = cache_ttl_seconds

    async def _search_provider(self, provider: ProductSearchProvider, query: str, limit: int):
        async with self._semaphore:
            try:
                return provider.name, await provider.search(query, limit=limit), None
            except ProviderUnavailableError as exc:
                logger.warning("provider_unavailable", provider=provider.name, error=str(exc))
                return provider.name, [], str(exc)
            except Exception as exc:  # noqa: BLE001
                logger.error("provider_unexpected_error", provider=provider.name, error=str(exc))
                return provider.name, [], "unexpected error"

    def _apply_filters(self, products: list[LiveProduct], filters: LiveSearchFilters) -> list[LiveProduct]:
        result = products
        if filters.marketplace is not None:
            result = [p for p in result if p.marketplace == filters.marketplace]
        if filters.min_price is not None:
            result = [p for p in result if p.price is not None and p.price >= filters.min_price]
        if filters.max_price is not None:
            result = [p for p in result if p.price is not None and p.price <= filters.max_price]
        if filters.min_rating is not None:
            result = [p for p in result if p.rating is not None and p.rating >= filters.min_rating]
        return result

    def _sort(self, products: list[LiveProduct], sort: LiveSortOption) -> list[LiveProduct]:
        key = _SORT_KEYS.get(sort)
        if key is None:  # relevance: keep provider order
            return products
        return sorted(products, key=key)

    async def search(self, filters: LiveSearchFilters) -> LiveSearchResponse:
        cache_key = build_cache_key(filters)

        if self._cache is not None:
            cached = await self._cache.get(cache_key)
            if cached is not None:
                logger.info("live_search_cache_hit", query=filters.query)
                response = LiveSearchResponse.model_validate_json(cached)
                response.cache_hit = True
                return response
            logger.info("live_search_cache_miss", query=filters.query)

        response = await self._execute_search(filters)

        if self._cache is not None:
            await self._cache.set(cache_key, response.model_dump_json(), self._cache_ttl_seconds)

        return response

    async def _execute_search(self, filters: LiveSearchFilters) -> LiveSearchResponse:
        parsed_query = await self._query_processor.parse(filters.query)
        provider_query = " ".join(parsed_query.keywords) or filters.query

        # Explicit filter query params win; a price/rating constraint Gemini
        # pulled out of the free-text query only fills in what the caller
        # didn't already specify explicitly.
        effective_filters = filters.model_copy(
            update={
                "min_price": filters.min_price if filters.min_price is not None else parsed_query.min_price,
                "max_price": filters.max_price if filters.max_price is not None else parsed_query.max_price,
            }
        )

        # Fetch enough per provider to cover the requested page, since
        # dedup/filtering happen after fetch and can't top back up a
        # too-small pool. Capped so a deep page doesn't fetch unbounded.
        fetch_limit = min(filters.page * filters.limit, 100)

        tasks = [
            self._search_provider(provider, provider_query, fetch_limit)
            for provider in self._providers
        ]
        outcomes = await asyncio.gather(*tasks) if tasks else []

        all_products: list[LiveProduct] = []
        marketplace_status: dict[str, str] = {}
        for provider_name, products, error in outcomes:
            marketplace_status[provider_name] = "unavailable" if error else "success"
            all_products.extend(products)

        all_products = deduplicate_live_products(all_products)
        all_products = self._apply_filters(all_products, effective_filters)
        all_products = self._sort(all_products, filters.sort)

        total = len(all_products)
        start = (filters.page - 1) * filters.limit
        page_results = all_products[start : start + filters.limit]

        return LiveSearchResponse(
            query=filters.query,
            parsed_query=parsed_query,
            total=total,
            page=filters.page,
            limit=filters.limit,
            results=page_results,
            marketplace_status=marketplace_status,
        )
