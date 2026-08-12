import json

import httpx
import pytest
import respx

from app.ai.query_processor import GeminiQueryProcessor
from app.core.config import Settings


def _gemini_response(payload: dict) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": json.dumps(payload)}]}}]}


@pytest.mark.asyncio
async def test_parse_falls_back_to_keywords_when_gemini_disabled():
    processor = GeminiQueryProcessor(Settings(gemini_api_key=""))
    result = await processor.parse("Samsung 55 inch 4K TV under 50000")

    assert "Samsung" in result.keywords
    assert result.brand is None
    assert result.max_price is None


@pytest.mark.asyncio
@respx.mock
async def test_parse_extracts_structured_intent():
    respx.post(url__regex=r".*generativelanguage\.googleapis\.com.*").mock(
        return_value=httpx.Response(
            200,
            json=_gemini_response(
                {
                    "keywords": ["Samsung", "55 inch", "4K", "TV"],
                    "brand": "Samsung",
                    "category": "television",
                    "max_price": 50000,
                }
            ),
        )
    )

    processor = GeminiQueryProcessor(Settings(gemini_api_key="test-key"))
    result = await processor.parse("Show me Samsung 55 inch 4K TVs under 50000")

    assert result.brand == "Samsung"
    assert result.category == "television"
    assert result.max_price == 50000
    assert "Samsung" in result.keywords


@pytest.mark.asyncio
@respx.mock
async def test_parse_falls_back_to_keywords_on_gemini_failure():
    respx.post(url__regex=r".*generativelanguage\.googleapis\.com.*").mock(return_value=httpx.Response(500))

    processor = GeminiQueryProcessor(Settings(gemini_api_key="test-key"))
    result = await processor.parse("nike shoes")

    assert result.keywords == ["nike", "shoes"]
