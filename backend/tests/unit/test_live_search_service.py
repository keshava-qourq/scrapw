from datetime import datetime, timezone

import pytest

from app.providers.base import ProductSearchProvider, ProviderUnavailableError
from app.schemas.live_search import Availability, LiveProduct, LiveSearchFilters, LiveSortOption, Marketplace
from app.services.live_search_service import LiveSearchService


def _product(title, price, rating, marketplace, product_id) -> LiveProduct:
    return LiveProduct(
        id=product_id,
        title=title,
        brand=None,
        marketplace=marketplace,
        price=price,
        rating=rating,
        product_url=f"https://example.com/{product_id}",
        source="fake",
        scraped_at=datetime.now(timezone.utc),
        availability=Availability.UNKNOWN,
    )


class FakeProvider(ProductSearchProvider):
    def __init__(self, name, products=None, fail=False):
        self.name = name
        self._products = products or []
        self._fail = fail

    async def search(self, query, limit=20):
        if self._fail:
            raise ProviderUnavailableError("boom")
        return self._products[:limit]


class FakeQueryProcessor:
    async def parse(self, raw_query):
        from app.schemas.live_search import ParsedQuery

        return ParsedQuery(keywords=raw_query.split())


class PriceParsingFakeQueryProcessor:
    """Simulates Gemini extracting a max_price from natural language that
    the caller didn't pass as an explicit filter param."""

    async def parse(self, raw_query):
        from app.schemas.live_search import ParsedQuery

        return ParsedQuery(keywords=raw_query.split(), max_price=80000)

        return ParsedQuery(keywords=raw_query.split())


@pytest.mark.asyncio
async def test_one_provider_failure_does_not_fail_others():
    amazon = FakeProvider("amazon", [_product("Shoe A", 100, 4.0, Marketplace.AMAZON, "1")])
    flipkart = FakeProvider("flipkart", fail=True)

    service = LiveSearchService([amazon, flipkart], FakeQueryProcessor())
    response = await service.search(LiveSearchFilters(query="shoes"))

    assert response.marketplace_status == {"amazon": "success", "flipkart": "unavailable"}
    assert response.total == 1


@pytest.mark.asyncio
async def test_filters_by_price_range():
    amazon = FakeProvider(
        "amazon",
        [
            _product("Cheap", 100, 4.0, Marketplace.AMAZON, "1"),
            _product("Expensive", 10000, 4.0, Marketplace.AMAZON, "2"),
        ],
    )
    service = LiveSearchService([amazon], FakeQueryProcessor())
    response = await service.search(LiveSearchFilters(query="x", max_price=500))

    assert response.total == 1
    assert response.results[0].id == "1"


@pytest.mark.asyncio
async def test_sorts_by_price_low_to_high():
    amazon = FakeProvider(
        "amazon",
        [
            _product("B", 300, 4.0, Marketplace.AMAZON, "2"),
            _product("A", 100, 4.0, Marketplace.AMAZON, "1"),
        ],
    )
    service = LiveSearchService([amazon], FakeQueryProcessor())
    response = await service.search(LiveSearchFilters(query="x", sort=LiveSortOption.PRICE_LOW_TO_HIGH))

    assert [p.id for p in response.results] == ["1", "2"]


@pytest.mark.asyncio
async def test_pagination():
    products = [_product(f"P{i}", i, 4.0, Marketplace.AMAZON, str(i)) for i in range(5)]
    amazon = FakeProvider("amazon", products)
    service = LiveSearchService([amazon], FakeQueryProcessor())
    response = await service.search(LiveSearchFilters(query="x", page=2, limit=2))

    # `total` reflects the pool actually fetched (bounded per provider), not
    # an omniscient marketplace-wide count — see LiveSearchService docstring.
    assert response.total == 4
    assert response.page == 2
    assert len(response.results) == 2
    assert [p.id for p in response.results] == ["2", "3"]


@pytest.mark.asyncio
async def test_no_providers_returns_empty():
    service = LiveSearchService([], FakeQueryProcessor())
    response = await service.search(LiveSearchFilters(query="x"))

    assert response.total == 0
    assert response.marketplace_status == {}


@pytest.mark.asyncio
async def test_gemini_parsed_max_price_is_actually_applied_as_a_filter():
    amazon = FakeProvider(
        "amazon",
        [
            _product("Cheap", 79999, 4.0, Marketplace.AMAZON, "1"),
            _product("Expensive", 102900, 4.0, Marketplace.AMAZON, "2"),
        ],
    )
    service = LiveSearchService([amazon], PriceParsingFakeQueryProcessor())
    response = await service.search(LiveSearchFilters(query="iPhone 17 under 80000"))

    assert response.total == 1
    assert response.results[0].id == "1"


@pytest.mark.asyncio
async def test_explicit_max_price_param_wins_over_gemini_parsed_one():
    amazon = FakeProvider(
        "amazon",
        [
            _product("A", 90000, 4.0, Marketplace.AMAZON, "1"),
            _product("B", 120000, 4.0, Marketplace.AMAZON, "2"),
        ],
    )
    service = LiveSearchService([amazon], PriceParsingFakeQueryProcessor())
    # Gemini parses max_price=80000, but the caller explicitly asked for 100000.
    response = await service.search(LiveSearchFilters(query="iPhone 17 under 80000", max_price=100000))

    assert response.total == 1
    assert response.results[0].id == "1"
