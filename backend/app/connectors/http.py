import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.exceptions import MarketplaceTimeoutError

_RETRIABLE_EXCEPTIONS = (httpx.TimeoutException, httpx.TransportError)


def build_http_client(timeout_seconds: float) -> httpx.AsyncClient:
    """Build a pooled, reusable httpx client. Callers should keep this alive
    for the lifetime of the connector rather than creating one per request."""
    return httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds), follow_redirects=True)


def with_retries(marketplace_code: str, retry_count: int):
    """Retry decorator with capped exponential backoff for transient network errors.
    Never retries indefinitely and never retries on 4xx (client/auth/bot-detection) errors."""

    def _reraise_as_marketplace_timeout(retry_state):
        exc = retry_state.outcome.exception()
        raise MarketplaceTimeoutError(marketplace_code, str(exc)) from exc

    return retry(
        stop=stop_after_attempt(max(retry_count, 1)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        retry=retry_if_exception_type(_RETRIABLE_EXCEPTIONS),
        retry_error_callback=_reraise_as_marketplace_timeout,
        reraise=False,
    )
