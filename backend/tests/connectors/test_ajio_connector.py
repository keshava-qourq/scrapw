import pytest

from app.connectors.ajio.connector import AjioConnector
from app.connectors.base import ConnectorConfig
from app.core.exceptions import MarketplaceNotConfiguredError


@pytest.fixture
def connector():
    return AjioConnector(ConnectorConfig(marketplace_code="ajio", enabled=False))


@pytest.mark.asyncio
async def test_search_products_returns_mock_matches(connector):
    results = await connector.search_products("nike")
    assert len(results) == 1


@pytest.mark.asyncio
async def test_normalize_product_includes_sizes_and_colors(connector):
    [raw] = await connector.search_products("nike")
    normalized = connector.normalize_product(raw)
    assert normalized["sizes"]
    assert normalized["colors"]


@pytest.mark.asyncio
async def test_enabled_always_raises_not_configured():
    conn = AjioConnector(ConnectorConfig(marketplace_code="ajio", enabled=True))
    with pytest.raises(MarketplaceNotConfiguredError):
        await conn.search_products("nike")
