from typing import Any

from app.connectors.base import ConnectorConfig, MarketplaceConnector, RawProduct
from app.connectors.flipkart.mapper import map_to_common_schema
from app.connectors.flipkart.parser import parse_flipkart_payload
from app.connectors.http import build_http_client
from app.connectors.rate_limiter import RateLimiter
from app.core.exceptions import MarketplaceNotConfiguredError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Clearly-labeled mock data mirroring a Flipkart Affiliate API feed entry.
# Used only while FLIPKART_API_ENABLED is false (the default).
_MOCK_CATALOG: list[dict[str, Any]] = [
    {
        "productId": "MOCKFK0001",
        "productUrl": "https://www.flipkart.com/mock/p/MOCKFK0001",
        "title": "Nike Revolution 7 Running Shoes (Mock Listing)",
        "productBrand": "Nike",
        "description": "Breathable running shoes with cushioned sole.",
        "categoryPath": "Footwear/Sports Shoes",
        "imageUrls": {"400x400": "https://example.com/mock/flipkart/nike-revolution-7.jpg"},
        "flipkartSellingPrice": {"amount": 4399.0, "currency": "INR"},
        "maximumRetailPrice": {"amount": 5995.0, "currency": "INR"},
        "inStock": True,
        "productRating": 4.2,
    }
]


class FlipkartConnector(MarketplaceConnector):
    """
    Real access path: Flipkart Affiliate API (product feeds), available after
    approval at https://affiliate.flipkart.com/. Configure FLIPKART_API_ENABLED=true,
    FLIPKART_API_KEY and FLIPKART_API_SECRET in .env to activate it.

    Until those are configured, this connector serves clearly-labeled mock data.
    """

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self._http = build_http_client(config.timeout_seconds)
        self._rate_limiter = RateLimiter(config.requests_per_second, config.max_concurrent_requests)

    async def aclose(self) -> None:
        await self._http.aclose()

    def _require_real_api(self) -> None:
        if not self.config.enabled or not self.config.api_key or not self.config.api_secret:
            raise MarketplaceNotConfiguredError(
                "flipkart",
                "Affiliate API credentials not configured. Set FLIPKART_API_ENABLED=true, "
                "FLIPKART_API_KEY and FLIPKART_API_SECRET to enable real Flipkart access. "
                "Falling back to mock data until then.",
            )

    async def search_products(self, query: str, **kwargs: Any) -> list[RawProduct]:
        if self.config.enabled:
            self._require_real_api()
            # TODO: implement Flipkart Affiliate API feed fetch + filter here.
            raise NotImplementedError("Flipkart Affiliate API integration not yet implemented")

        logger.info("flipkart_connector_mock_search", query=query)
        query_lower = query.lower()
        matches = [item for item in _MOCK_CATALOG if query_lower in item["title"].lower() or not query_lower]
        return [
            RawProduct(item["productId"], item["productUrl"], item) for item in matches
        ]

    async def fetch_product(self, url: str) -> RawProduct | None:
        if self.config.enabled:
            self._require_real_api()
            raise NotImplementedError("Flipkart Affiliate API integration not yet implemented")

        for item in _MOCK_CATALOG:
            if item["productUrl"] == url:
                return RawProduct(item["productId"], item["productUrl"], item)
        return None

    async def fetch_product_details(self, product_id: str) -> RawProduct | None:
        if self.config.enabled:
            self._require_real_api()
            raise NotImplementedError("Flipkart Affiliate API integration not yet implemented")

        for item in _MOCK_CATALOG:
            if item["productId"] == product_id:
                return RawProduct(item["productId"], item["productUrl"], item)
        return None

    def normalize_product(self, raw_product: RawProduct) -> dict[str, Any]:
        parsed = parse_flipkart_payload(raw_product.payload)
        return map_to_common_schema(parsed, raw_product.marketplace_product_id, raw_product.product_url)
