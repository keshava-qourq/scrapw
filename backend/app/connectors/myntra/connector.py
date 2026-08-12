from typing import Any

from app.connectors.base import ConnectorConfig, MarketplaceConnector, RawProduct
from app.connectors.http import build_http_client
from app.connectors.myntra.mapper import map_to_common_schema
from app.connectors.myntra.parser import parse_myntra_payload
from app.connectors.rate_limiter import RateLimiter
from app.core.exceptions import MarketplaceNotConfiguredError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Myntra has no publicly documented affiliate/partner product-data API at the
# time this connector was written. This connector always serves mock data
# until a permitted access mechanism is identified and configured.
_MOCK_CATALOG: list[dict[str, Any]] = [
    {
        "productId": "MOCKMYN0001",
        "productUrl": "https://www.myntra.com/mock/p/MOCKMYN0001",
        "name": "Nike Men Revolution 7 Running Shoes (Mock Listing)",
        "brand": "Nike",
        "description": "Soft cushioning with breathable mesh upper.",
        "category": "Footwear/Sports Shoes",
        "imageUrl": "https://example.com/mock/myntra/nike-revolution-7.jpg",
        "price": 4299.0,
        "mrp": 5995.0,
        "currency": "INR",
        "inStock": True,
        "rating": 4.4,
        "reviewCount": 1200,
        "sizes": ["UK6", "UK7", "UK8", "UK9"],
        "colors": ["Blue", "Black"],
    }
]


class MyntraConnector(MarketplaceConnector):
    """
    No known official API or affiliate feed is currently available for Myntra.
    This connector always serves mock data and documents what would be needed
    to plug in a real integration: a signed partner agreement with Myntra
    granting API/feed access, plus credentials configured via MYNTRA_API_KEY /
    MYNTRA_API_SECRET and MYNTRA_API_ENABLED=true.
    """

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self._http = build_http_client(config.timeout_seconds)
        self._rate_limiter = RateLimiter(config.requests_per_second, config.max_concurrent_requests)

    async def aclose(self) -> None:
        await self._http.aclose()

    def _warn_if_enabled_without_integration(self) -> None:
        if self.config.enabled:
            raise MarketplaceNotConfiguredError(
                "myntra",
                "No permitted Myntra API/feed integration is implemented yet. "
                "Falling back to mock data until an official access mechanism is available.",
            )

    async def search_products(self, query: str, **kwargs: Any) -> list[RawProduct]:
        self._warn_if_enabled_without_integration()
        logger.info("myntra_connector_mock_search", query=query)
        query_lower = query.lower()
        matches = [item for item in _MOCK_CATALOG if query_lower in item["name"].lower() or not query_lower]
        return [RawProduct(item["productId"], item["productUrl"], item) for item in matches]

    async def fetch_product(self, url: str) -> RawProduct | None:
        self._warn_if_enabled_without_integration()
        for item in _MOCK_CATALOG:
            if item["productUrl"] == url:
                return RawProduct(item["productId"], item["productUrl"], item)
        return None

    async def fetch_product_details(self, product_id: str) -> RawProduct | None:
        self._warn_if_enabled_without_integration()
        for item in _MOCK_CATALOG:
            if item["productId"] == product_id:
                return RawProduct(item["productId"], item["productUrl"], item)
        return None

    def normalize_product(self, raw_product: RawProduct) -> dict[str, Any]:
        parsed = parse_myntra_payload(raw_product.payload)
        return map_to_common_schema(parsed, raw_product.marketplace_product_id, raw_product.product_url)
