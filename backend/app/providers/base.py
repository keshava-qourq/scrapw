from abc import ABC, abstractmethod

from app.schemas.live_search import LiveProduct


class ProviderUnavailableError(Exception):
    """Raised when a provider can't be queried right now (bad key, rate limit,
    timeout, network error). Caught by the orchestrator so one provider
    failing never fails the whole search."""


class ProductSearchProvider(ABC):
    """
    Common interface every live-search data source implements — SerpApi
    today, direct marketplace APIs later if/when they're available under
    proper agreements. `LiveSearchService` only ever depends on this
    interface, never on a concrete provider.
    """

    name: str

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[LiveProduct]:
        """Return normalized products for `query`. Raise
        `ProviderUnavailableError` on any failure rather than returning
        partial/fabricated data."""

    async def close(self) -> None:
        """Release any held resources (HTTP clients, browser contexts, ...).
        Default no-op; override if the provider holds something open."""
