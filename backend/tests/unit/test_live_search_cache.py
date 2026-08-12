from datetime import datetime, timezone

import pytest

from app.cache.search_cache import SearchCache, build_cache_key
from app.providers.base import ProductSearchProvider
from app.schemas.live_search import Availability, LiveProduct, LiveSearchFilters, Marketplace
from app.services.live_search_service import LiveSearchService


class InMemorySearchCache(SearchCache):
    def __init__(self):
        self.store: dict[str, str] = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ttl_seconds):
        self.store[key] = value


class CountingProvider(ProductSearchProvider):
    name = "amazon"

    def __init__(self):
        self.call_count = 0

    async def search(self, query, limit=20):
        self.call_count += 1
        return [
            LiveProduct(
                id="1",
                title="Nike Shoes",
                marketplace=Marketplace.AMAZON,
                product_url="https://example.com/1",
                source="fake",
                scraped_at=datetime.now(timezone.utc),
                availability=Availability.UNKNOWN,
            )
        ]


class FakeQueryProcessor:
    async def parse(self, raw_query):
        from app.schemas.live_search import ParsedQuery

        return ParsedQuery(keywords=raw_query.split())


@pytest.mark.asyncio
async def test_second_identical_search_hits_cache_not_provider():
    provider = CountingProvider()
    cache = InMemorySearchCache()
    service = LiveSearchService([provider], FakeQueryProcessor(), cache=cache, cache_ttl_seconds=900)
    filters = LiveSearchFilters(query="nike shoes")

    first = await service.search(filters)
    second = await service.search(filters)

    assert provider.call_count == 1
    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.total == first.total


@pytest.mark.asyncio
async def test_different_filters_produce_different_cache_keys():
    key_a = build_cache_key(LiveSearchFilters(query="nike shoes", max_price=1000))
    key_b = build_cache_key(LiveSearchFilters(query="nike shoes", max_price=2000))

    assert key_a != key_b
