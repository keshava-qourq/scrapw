import hashlib
import json
from abc import ABC, abstractmethod

from redis.asyncio import Redis

from app.schemas.live_search import LiveSearchFilters


def build_cache_key(filters: LiveSearchFilters) -> str:
    """Deterministic key for a query+filters combination, so identical
    searches (including identical filter values) share a cache entry."""
    payload = filters.model_dump(mode="json")
    normalized = json.dumps(payload, sort_keys=True)
    digest = hashlib.sha256(normalized.encode()).hexdigest()[:24]
    return f"live_search:{digest}"


class SearchCache(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int) -> None: ...


class RedisSearchCache(SearchCache):
    """Cache backend for live search responses. Reuses the same Redis
    instance already provisioned for Celery — no new infrastructure."""

    def __init__(self, redis_url: str):
        self._client = Redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._client.set(key, value, ex=ttl_seconds)
