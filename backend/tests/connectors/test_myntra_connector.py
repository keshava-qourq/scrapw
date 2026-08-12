import pytest

from app.connectors.base import ConnectorConfig
from app.connectors.myntra.connector import MyntraConnector
from app.core.exceptions import MarketplaceNotConfiguredError


@pytest.fixture
def connector():
    return MyntraConnector(ConnectorConfig(marketplace_code="myntra", enabled=False))


@pytest.mark.asyncio
async def test_search_products_returns_mock_matches(connector):
    results = await connector.search_products("nike")
    assert len(results) == 1


@pytest.mark.asyncio
async def test_normalize_product_maps_common_schema(connector):
    [raw] = await connector.search_products("nike")
    normalized = connector.normalize_product(raw)
    assert normalized["marketplace_code"] == "myntra"
    assert normalized["price"] == 4299.0


@pytest.mark.asyncio
async def test_enabled_always_raises_not_configured():
    conn = MyntraConnector(ConnectorConfig(marketplace_code="myntra", enabled=True))
    with pytest.raises(MarketplaceNotConfiguredError):
        await conn.search_products("nike")
