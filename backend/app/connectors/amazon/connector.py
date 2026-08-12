from typing import Any

from app.connectors.amazon.mapper import map_to_common_schema
from app.connectors.amazon.parser import parse_amazon_payload
from app.connectors.base import ConnectorConfig, MarketplaceConnector, RawProduct
from app.connectors.http import build_http_client
from app.connectors.rate_limiter import RateLimiter
from app.core.exceptions import MarketplaceNotConfiguredError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Deterministic, clearly-labeled fixture data used only when AMAZON_API_ENABLED
# is false (the default). Mirrors the shape of a real PA-API 5.0 `Item`. This is
# NOT scraped or fabricated marketplace data — it exists purely so the rest of
# the pipeline (normalization, dedup, indexing, search) has something to run
# against in local/dev environments without real credentials.
_MOCK_CATALOG: list[dict[str, Any]] = [
    {
        "ASIN": "MOCKASIN0001",
        "DetailPageURL": "https://www.amazon.in/mock/dp/MOCKASIN0001",
        "ItemInfo": {
            "Title": {"DisplayValue": "Nike Revolution 7 Men's Running Shoes (Mock Listing)"},
            "ByLineInfo": {"Brand": {"DisplayValue": "Nike"}},
            "Features": {"DisplayValues": ["Lightweight mesh upper", "Foam midsole"]},
        },
        "Images": {"Primary": {"Large": {"URL": "https://example.com/mock/amazon/nike-revolution-7.jpg"}}},
        "Offers": {
            "Listings": [
                {
                    "Price": {"Amount": 4499.0, "Currency": "INR"},
                    "SavingBasis": {"Amount": 5995.0, "Currency": "INR"},
                    "Availability": {"Type": "Now"},
                }
            ]
        },
        "CustomerReviews": {"StarRating": 4.3, "Count": 812},
    }
]


class AmazonConnector(MarketplaceConnector):
    """
    Real access path: Amazon Product Advertising API (PA-API 5.0), available to
    approved Amazon Associates. See https://webservices.amazon.com/paapi5/documentation/
    Configure AMAZON_API_ENABLED=true, AMAZON_API_KEY, AMAZON_API_SECRET and
    AMAZON_PARTNER_TAG in .env to activate it.

    Until those are configured, this connector serves clearly-labeled mock data
    so the ingestion pipeline can be exercised end-to-end.
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
                "amazon",
                "PA-API credentials not configured. Set AMAZON_API_ENABLED=true, "
                "AMAZON_API_KEY, AMAZON_API_SECRET and AMAZON_PARTNER_TAG to enable "
                "real Amazon access. Falling back to mock data until then.",
            )

    async def search_products(self, query: str, **kwargs: Any) -> list[RawProduct]:
        if self.config.enabled:
            self._require_real_api()
            # TODO: implement PA-API 5.0 SearchItems request signing + call here,
            # using self._http and self._rate_limiter for pooled/rate-limited access.
            raise NotImplementedError("Amazon PA-API integration not yet implemented")

        logger.info("amazon_connector_mock_search", query=query)
        query_lower = query.lower()
        matches = [
            item
            for item in _MOCK_CATALOG
            if query_lower in item["ItemInfo"]["Title"]["DisplayValue"].lower()
            or not query_lower
        ]
        return [
            RawProduct(
                marketplace_product_id=item["ASIN"],
                product_url=item["DetailPageURL"],
                payload=item,
            )
            for item in matches
        ]

    async def fetch_product(self, url: str) -> RawProduct | None:
        if self.config.enabled:
            self._require_real_api()
            raise NotImplementedError("Amazon PA-API integration not yet implemented")

        for item in _MOCK_CATALOG:
            if item["DetailPageURL"] == url:
                return RawProduct(item["ASIN"], item["DetailPageURL"], item)
        return None

    async def fetch_product_details(self, product_id: str) -> RawProduct | None:
        if self.config.enabled:
            self._require_real_api()
            raise NotImplementedError("Amazon PA-API integration not yet implemented")

        for item in _MOCK_CATALOG:
            if item["ASIN"] == product_id:
                return RawProduct(item["ASIN"], item["DetailPageURL"], item)
        return None

    def normalize_product(self, raw_product: RawProduct) -> dict[str, Any]:
        parsed = parse_amazon_payload(raw_product.payload)
        return map_to_common_schema(parsed, raw_product.marketplace_product_id, raw_product.product_url)
