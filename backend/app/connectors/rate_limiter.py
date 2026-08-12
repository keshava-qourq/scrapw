import asyncio
import time


class RateLimiter:
    """Simple token-bucket limiter combined with a concurrency semaphore.

    Shared by every connector so ingestion never exceeds the conservative
    per-marketplace defaults in ConnectorConfig.
    """

    def __init__(self, requests_per_second: float, max_concurrent_requests: int):
        self._min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0.0
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def __aenter__(self) -> "RateLimiter":
        await self._semaphore.acquire()
        async with self._lock:
            now = time.monotonic()
            wait_for = self._last_request_at + self._min_interval - now
            if wait_for > 0:
                await asyncio.sleep(wait_for)
            self._last_request_at = time.monotonic()
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        self._semaphore.release()
