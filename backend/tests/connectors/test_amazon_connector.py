import pytest

from app.connectors.amazon.connector import AmazonConnector
from app.connectors.base import ConnectorConfig
from app.core.exceptions import MarketplaceNotConfiguredError
from app.models.product import AvailabilityStatus


@pytest.fixture
def connector():
    config = ConnectorConfig(marketplace_code="amazon", enabled=False)
    conn = AmazonConnector(config)
    yield conn


@pytest.mark.asyncio
async def test_search_products_returns_mock_matches(connector):
    results = await connector.search_products("nike")
    assert len(results) == 1
    assert results[0].marketplace_product_id == "MOCKASIN0001"


@pytest.mark.asyncio
async def test_search_products_no_match_returns_empty(connector):
    results = await connector.search_products("totally-unrelated-query-xyz")
    assert results == []


@pytest.mark.asyncio
async def test_fetch_product_details_by_id(connector):
    raw = await connector.fetch_product_details("MOCKASIN0001")
    assert raw is not None
    assert raw.marketplace_product_id == "MOCKASIN0001"


@pytest.mark.asyncio
async def test_normalize_product_maps_common_schema(connector):
    [raw] = await connector.search_products("")
    normalized = connector.normalize_product(raw)

    assert normalized["marketplace_code"] == "amazon"
    assert normalized["name"] == "Nike Revolution 7 Men's Running Shoes (Mock Listing)"
    assert normalized["brand"] == "Nike"
    assert normalized["price"] == 4499.0
    assert normalized["mrp"] == 5995.0
    assert normalized["availability"] == AvailabilityStatus.IN_STOCK
    assert normalized["discount_percentage"] == pytest.approx(24.95, abs=0.01)


@pytest.mark.asyncio
async def test_enabled_without_credentials_raises_not_configured():
    config = ConnectorConfig(marketplace_code="amazon", enabled=True, api_key="", api_secret="")
    conn = AmazonConnector(config)
    with pytest.raises(MarketplaceNotConfiguredError):
        await conn.search_products("nike")
