from typing import Any

from opensearchpy import AsyncOpenSearch, NotFoundError as OpenSearchNotFoundError

from app.core.config import Settings
from app.core.exceptions import SearchIndexError
from app.core.logging import get_logger
from app.schemas.search import SortOption
from app.search.base import SearchIndex

logger = get_logger(__name__)

_INDEX_MAPPING = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "brand": {"type": "keyword"},
            "category": {"type": "keyword"},
            "description": {"type": "text"},
            "marketplace": {"type": "keyword"},
            "price": {"type": "double"},
            "mrp": {"type": "double"},
            "discount_percentage": {"type": "double"},
            "rating": {"type": "double"},
            "review_count": {"type": "integer"},
            "availability": {"type": "keyword"},
            "sizes": {"type": "keyword"},
            "colors": {"type": "keyword"},
            "image_url": {"type": "keyword", "index": False},
            "product_url": {"type": "keyword", "index": False},
            "last_updated_at": {"type": "date"},
        }
    },
}

_SORT_MAP = {
    SortOption.PRICE_LOW_TO_HIGH: [{"price": {"order": "asc", "missing": "_last"}}],
    SortOption.PRICE_HIGH_TO_LOW: [{"price": {"order": "desc", "missing": "_last"}}],
    SortOption.RATING: [{"rating": {"order": "desc", "missing": "_last"}}],
    SortOption.DISCOUNT: [{"discount_percentage": {"order": "desc", "missing": "_last"}}],
    SortOption.NEWEST: [{"last_updated_at": {"order": "desc", "missing": "_last"}}],
}


class OpenSearchIndex(SearchIndex):
    def __init__(self, settings: Settings):
        self._index = settings.opensearch_product_index
        auth = None
        if settings.opensearch_username:
            auth = (settings.opensearch_username, settings.opensearch_password)
        self._client = AsyncOpenSearch(
            hosts=[settings.opensearch_url],
            http_auth=auth,
            use_ssl=settings.opensearch_use_ssl,
            verify_certs=settings.opensearch_verify_certs,
        )

    async def ensure_index(self) -> None:
        exists = await self._client.indices.exists(index=self._index)
        if not exists:
            await self._client.indices.create(index=self._index, body=_INDEX_MAPPING)
            logger.info("search_index_created", index=self._index)

    async def index_product(self, product_id: str, document: dict[str, Any]) -> None:
        try:
            await self._client.index(index=self._index, id=product_id, body=document, refresh=False)
        except Exception as exc:  # noqa: BLE001
            raise SearchIndexError(f"Failed to index product {product_id}: {exc}") from exc

    async def bulk_index_products(self, documents: list[dict[str, Any]]) -> None:
        if not documents:
            return
        actions = []
        for doc in documents:
            actions.append({"index": {"_index": self._index, "_id": doc["id"]}})
            actions.append(doc)
        try:
            response = await self._client.bulk(body=actions)
        except Exception as exc:  # noqa: BLE001
            raise SearchIndexError(f"Bulk indexing failed: {exc}") from exc
        if response.get("errors"):
            logger.error("search_bulk_index_partial_failure", response=response)

    async def delete_product(self, product_id: str) -> None:
        try:
            await self._client.delete(index=self._index, id=product_id)
        except OpenSearchNotFoundError:
            pass
        except Exception as exc:  # noqa: BLE001
            raise SearchIndexError(f"Failed to delete product {product_id}: {exc}") from exc

    async def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        sort: str = "relevance",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        must: list[dict[str, Any]] = [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "brand^2", "description"],
                    "fuzziness": "AUTO",
                }
            }
        ]
        filter_clauses: list[dict[str, Any]] = []
        filters = filters or {}

        term_filters = {
            "marketplace": "marketplace",
            "brand": "brand",
            "category": "category",
            "availability": "availability",
        }
        for key, field in term_filters.items():
            if filters.get(key):
                filter_clauses.append({"term": {field: filters[key]}})

        if filters.get("size"):
            filter_clauses.append({"term": {"sizes": filters["size"]}})
        if filters.get("color"):
            filter_clauses.append({"term": {"colors": filters["color"]}})

        price_range = {}
        if filters.get("min_price") is not None:
            price_range["gte"] = filters["min_price"]
        if filters.get("max_price") is not None:
            price_range["lte"] = filters["max_price"]
        if price_range:
            filter_clauses.append({"range": {"price": price_range}})

        if filters.get("min_rating") is not None:
            filter_clauses.append({"range": {"rating": {"gte": filters["min_rating"]}}})
        if filters.get("min_discount") is not None:
            filter_clauses.append({"range": {"discount_percentage": {"gte": filters["min_discount"]}}})

        body: dict[str, Any] = {
            "query": {"bool": {"must": must, "filter": filter_clauses}},
            "from": (page - 1) * page_size,
            "size": page_size,
        }

        sort_option = SortOption(sort) if not isinstance(sort, SortOption) else sort
        if sort_option in _SORT_MAP:
            body["sort"] = _SORT_MAP[sort_option]

        try:
            response = await self._client.search(index=self._index, body=body)
        except Exception as exc:  # noqa: BLE001
            raise SearchIndexError(f"Search query failed: {exc}") from exc

        hits = [hit["_source"] | {"id": hit["_id"]} for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]
        return hits, total

    async def close(self) -> None:
        await self._client.close()
