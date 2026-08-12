import pytest

from app.connectors.base import ConnectorConfig
from app.connectors.flipkart.connector import FlipkartConnector


@pytest.fixture
def connector():
    return FlipkartConnector(ConnectorConfig(marketplace_code="flipkart", enabled=False))


@pytest.mark.asyncio
async def test_search_products_returns_mock_matches(connector):
    results = await connector.search_products("nike")
    assert len(results) == 1
    assert results[0].marketplace_product_id == "MOCKFK0001"


@pytest.mark.asyncio
async def test_normalize_product_maps_common_schema(connector):
    [raw] = await connector.search_products("nike")
    normalized = connector.normalize_product(raw)

    assert normalized["marketplace_code"] == "flipkart"
    assert normalized["brand"] == "Nike"
    assert normalized["price"] == 4399.0
    assert normalized["mrp"] == 5995.0
