import json

import httpx
import pytest
import respx

from app.core.config import Settings
from app.schemas.search import SortOption
from app.services.query_understanding_service import QueryUnderstandingService


def _settings(**overrides) -> Settings:
    return Settings(gemini_api_key="test-key", gemini_model="gemini-2.0-flash", **overrides)


def _gemini_response(payload: dict) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": json.dumps(payload)}]}}]}


@pytest.mark.asyncio
async def test_parse_returns_plain_query_when_disabled():
    service = QueryUnderstandingService(Settings(gemini_api_key=""))
    filters = await service.parse("nike running shoes")

    assert filters.query == "nike running shoes"
    assert filters.marketplace is None
    assert filters.sort == SortOption.RELEVANCE


@pytest.mark.asyncio
@respx.mock
async def test_parse_extracts_filters_from_gemini_response():
    respx.post(url__regex=r".*generativelanguage\.googleapis\.com.*").mock(
        return_value=httpx.Response(
            200,
            json=_gemini_response(
                {
                    "query": "nike running shoes",
                    "brand": "Nike",
                    "max_price": 5000,
                    "min_rating": 4.0,
                    "sort": "price_low_to_high",
                }
            ),
        )
    )

    service = QueryUnderstandingService(_settings())
    filters = await service.parse("cheap nike running shoes under 5000 with good reviews")

    assert filters.query == "nike running shoes"
    assert filters.brand == "Nike"
    assert filters.max_price == 5000
    assert filters.min_rating == 4.0
    assert filters.sort == SortOption.PRICE_LOW_TO_HIGH


@pytest.mark.asyncio
@respx.mock
async def test_parse_falls_back_on_http_error():
    respx.post(url__regex=r".*generativelanguage\.googleapis\.com.*").mock(
        return_value=httpx.Response(500)
    )

    service = QueryUnderstandingService(_settings())
    filters = await service.parse("nike running shoes")

    assert filters.query == "nike running shoes"
    assert filters.marketplace is None


@pytest.mark.asyncio
@respx.mock
async def test_parse_falls_back_on_malformed_json():
    respx.post(url__regex=r".*generativelanguage\.googleapis\.com.*").mock(
        return_value=httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": "not json"}]}}]},
        )
    )

    service = QueryUnderstandingService(_settings())
    filters = await service.parse("nike running shoes")

    assert filters.query == "nike running shoes"
