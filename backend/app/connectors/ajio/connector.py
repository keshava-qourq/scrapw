from typing import Any

from app.connectors.ajio.mapper import map_to_common_schema
from app.connectors.ajio.parser import parse_ajio_payload
from app.connectors.base import ConnectorConfig, MarketplaceConnector, RawProduct
from app.connectors.http import build_http_client
from app.connectors.rate_limiter import RateLimiter
from app.core.exceptions import MarketplaceNotConfiguredError
from app.core.logging import get_logger

logger = get_logger(__name__)

# AJIO has no publicly documented affiliate/partner product-data API at the
# time this connector was written. This connector always runs in mock mode
# with clearly-labeled fixture data until a permitted access mechanism
# (official API, partner feed, etc.) is identified and configured.
_MOCK_CATALOG: list[dict[str, Any]] = [
    {
        "productId": "MOCKAJIO0001",
        "productUrl": "https://www.ajio.com/mock/p/MOCKAJIO0001",
        "name": "Nike Revolution 7 Men Running Shoes (Mock Listing)",
        "brand": "Nike",
        "description": "Cushioned running shoes for everyday training.",
        "category": "Footwear/Sports Shoes",
        "imageUrl": "https://example.com/mock/ajio/nike-revolution-7.jpg",
        "price": 4599.0,
        "mrp": 5995.0,
        "currency": "INR",
        "inStock": True,
        "rating": 4.1,
        "reviewCount": 340,
        "sizes": ["UK7", "UK8", "UK9", "UK10"],
        "colors": ["Black", "White"],
    }
]


class AjioConnector(MarketplaceConnector):
    """
    No known official API or affiliate feed is currently available for AJIO.
    This connector always serves mock data and documents what would be needed
    to plug in a real integration: a signed partner agreement with AJIO
    granting API/feed access, plus credentials configured via AJIO_API_KEY /
    AJIO_API_SECRET and AJIO_API_ENABLED=true.
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
                "ajio",
                "No permitted AJIO API/feed integration is implemented yet. "
                "Falling back to mock data until an official access mechanism is available.",
            )

    async def search_products(self, query: str, **kwargs: Any) -> list[RawProduct]:
        self._warn_if_enabled_without_integration()
        logger.info("ajio_connector_mock_search", query=query)
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
        parsed = parse_ajio_payload(raw_product.payload)
        return map_to_common_schema(parsed, raw_product.marketplace_product_id, raw_product.product_url)
