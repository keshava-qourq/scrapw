from collections.abc import AsyncGenerator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.query_processor import GeminiQueryProcessor
from app.cache.search_cache import RedisSearchCache, SearchCache
from app.core.config import Settings, get_settings
from app.db.database import get_db
from app.providers.base import ProductSearchProvider
from app.providers.serpapi_provider import SerpApiProductSearchProvider
from app.repositories.search_repository import SearchRepository
from app.search.base import SearchIndex
from app.search.opensearch import OpenSearchIndex
from app.services.card_offer_service import CardOfferService
from app.services.live_search_service import LiveSearchService
from app.services.product_service import ProductService
from app.services.query_understanding_service import QueryUnderstandingService
from app.services.search_service import SearchService


@lru_cache
def get_search_index() -> SearchIndex:
    """Process-wide OpenSearch client. Reused across requests instead of
    opening a new connection per call."""
    return OpenSearchIndex(get_settings())


async def get_search_service(
    search_index: SearchIndex = Depends(get_search_index),
) -> AsyncGenerator[SearchService, None]:
    yield SearchService(search_index)


async def get_product_service(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ProductService, None]:
    yield ProductService(session)


def get_app_settings() -> Settings:
    return get_settings()


def get_query_understanding_service(
    settings: Settings = Depends(get_app_settings),
) -> QueryUnderstandingService:
    return QueryUnderstandingService(settings)


@lru_cache
def get_search_cache() -> SearchCache:
    """Process-wide Redis client for live-search caching — reuses the same
    Redis instance already provisioned for Celery."""
    return RedisSearchCache(get_settings().redis_url)


def get_live_search_providers(settings: Settings = Depends(get_app_settings)) -> list[ProductSearchProvider]:
    """
    Registry of enabled live-search providers. SerpApi is the only one for
    the MVP; adding a direct marketplace provider later (under a proper
    agreement) is another entry here, not a change to LiveSearchService.
    """
    providers: list[ProductSearchProvider] = []
    if settings.serpapi_api_key:
        providers.append(SerpApiProductSearchProvider(settings))
    return providers


def get_gemini_query_processor(settings: Settings = Depends(get_app_settings)) -> GeminiQueryProcessor:
    return GeminiQueryProcessor(settings)


def get_live_search_service(
    settings: Settings = Depends(get_app_settings),
    providers: list[ProductSearchProvider] = Depends(get_live_search_providers),
    query_processor: GeminiQueryProcessor = Depends(get_gemini_query_processor),
    cache: SearchCache = Depends(get_search_cache),
) -> LiveSearchService:
    return LiveSearchService(
        providers,
        query_processor,
        max_concurrent_providers=settings.max_concurrent_providers,
        cache=cache,
        cache_ttl_seconds=settings.search_cache_ttl_seconds,
    )


async def get_search_repository(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[SearchRepository, None]:
    yield SearchRepository(session)


async def get_card_offer_service(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[CardOfferService, None]:
    yield CardOfferService(session)
