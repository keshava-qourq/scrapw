import httpx

from app.core.config import Settings
from app.core.logging import get_logger
from app.providers.base import ProductSearchProvider, ProviderUnavailableError
from app.schemas.live_search import LiveProduct
from app.services.product_normalizer import normalize_serpapi_shopping_result

logger = get_logger(__name__)

_SEARCH_URL = "https://serpapi.com/search"


class SerpApiProductSearchProvider(ProductSearchProvider):
    """
    MVP data source: SerpApi's `google_shopping` engine. A licensed
    aggregator, not a direct marketplace scraper — this is what lets the
    search engine return real cross-marketplace results without needing
    Amazon/Flipkart affiliate approval or touching AJIO/Myntra (which have
    no public API) directly.
    """

    name = "serpapi"

    def __init__(self, settings: Settings):
        self._settings = settings

    async def search(self, query: str, limit: int = 20) -> list[LiveProduct]:
        if not self._settings.serpapi_api_key:
            raise ProviderUnavailableError("SERPAPI_API_KEY not configured")

        params = {
            "engine": self._settings.serpapi_engine,
            "q": query,
            "api_key": self._settings.serpapi_api_key,
            "gl": "in",
            "hl": "en",
        }

        try:
            async with httpx.AsyncClient(timeout=self._settings.serpapi_timeout_seconds) as client:
                response = await client.get(_SEARCH_URL, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning("serpapi_http_error", status=exc.response.status_code, query=query)
            raise ProviderUnavailableError(f"SerpApi returned {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            logger.warning("serpapi_request_failed", error=str(exc), query=query)
            raise ProviderUnavailableError("SerpApi request failed") from exc

        if error := payload.get("error"):
            logger.warning("serpapi_error_response", error=error, query=query)
            raise ProviderUnavailableError(f"SerpApi error: {error}")

        raw_results = payload.get("shopping_results", [])
        products: list[LiveProduct] = []
        for item in raw_results[:limit]:
            product = normalize_serpapi_shopping_result(item, source=self.name)
            if product is not None:
                products.append(product)

        return products
