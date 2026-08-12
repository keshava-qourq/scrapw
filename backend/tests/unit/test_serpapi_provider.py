import httpx
import pytest
import respx

from app.core.config import Settings
from app.providers.base import ProviderUnavailableError
from app.providers.serpapi_provider import SerpApiProductSearchProvider


def _settings(**overrides) -> Settings:
    return Settings(serpapi_api_key="test-key", **overrides)


@pytest.mark.asyncio
async def test_search_raises_when_not_configured():
    provider = SerpApiProductSearchProvider(Settings(serpapi_api_key=""))
    with pytest.raises(ProviderUnavailableError):
        await provider.search("nike shoes")


@pytest.mark.asyncio
@respx.mock
async def test_search_normalizes_shopping_results():
    respx.get("https://serpapi.com/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "shopping_results": [
                    {
                        "title": "Nike Revolution 7",
                        "product_link": "https://www.amazon.in/dp/B0ABC123",
                        "source": "Amazon.in",
                        "extracted_price": 4499.0,
                        "rating": 4.3,
                        "reviews": 100,
                        "product_id": "B0ABC123",
                    },
                    {"title": "Missing link, should be dropped"},
                ]
            },
        )
    )

    provider = SerpApiProductSearchProvider(_settings())
    results = await provider.search("nike shoes")

    assert len(results) == 1
    assert results[0].title == "Nike Revolution 7"
    assert results[0].source == "serpapi"


@pytest.mark.asyncio
@respx.mock
async def test_search_raises_on_http_error():
    respx.get("https://serpapi.com/search").mock(return_value=httpx.Response(500))

    provider = SerpApiProductSearchProvider(_settings())
    with pytest.raises(ProviderUnavailableError):
        await provider.search("nike shoes")


@pytest.mark.asyncio
@respx.mock
async def test_search_raises_on_serpapi_error_payload():
    respx.get("https://serpapi.com/search").mock(
        return_value=httpx.Response(200, json={"error": "Invalid API key"})
    )

    provider = SerpApiProductSearchProvider(_settings())
    with pytest.raises(ProviderUnavailableError):
        await provider.search("nike shoes")


@pytest.mark.asyncio
@respx.mock
async def test_search_respects_limit():
    items = [
        {
            "title": f"Product {i}",
            "product_link": f"https://example.com/p/{i}",
            "product_id": str(i),
        }
        for i in range(5)
    ]
    respx.get("https://serpapi.com/search").mock(
        return_value=httpx.Response(200, json={"shopping_results": items})
    )

    provider = SerpApiProductSearchProvider(_settings())
    results = await provider.search("nike shoes", limit=2)

    assert len(results) == 2
