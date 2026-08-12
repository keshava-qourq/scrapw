from abc import ABC, abstractmethod
from typing import Any


class SearchIndex(ABC):
    """
    Interface for the product search backend. Concrete implementations (OpenSearch,
    Elasticsearch, or anything else) live behind this so the rest of the app never
    imports a search-engine-specific client directly.
    """

    @abstractmethod
    async def index_product(self, product_id: str, document: dict[str, Any]) -> None:
        """Create or replace the indexed document for a single product."""

    @abstractmethod
    async def bulk_index_products(self, documents: list[dict[str, Any]]) -> None:
        """Create or replace indexed documents for many products at once."""

    @abstractmethod
    async def delete_product(self, product_id: str) -> None:
        """Remove a product from the index."""

    @abstractmethod
    async def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        sort: str = "relevance",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """Run a search and return (hits, total_count)."""

    @abstractmethod
    async def ensure_index(self) -> None:
        """Create the index with the expected mapping if it doesn't already exist."""
