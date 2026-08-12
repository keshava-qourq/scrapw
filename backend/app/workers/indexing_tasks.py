import uuid

from celery import shared_task

from app.core.config import get_settings
from app.core.exceptions import SearchIndexError
from app.core.logging import get_logger
from app.repositories.product_repository import ProductRepository
from app.search.opensearch import OpenSearchIndex
from app.services.search_service import product_to_search_document
from app.workers.utils import run_async, worker_session

logger = get_logger(__name__)


@shared_task(bind=True, max_retries=5, retry_backoff=True, retry_backoff_max=120, retry_jitter=True)
def index_products(self, product_ids: list[str]) -> None:
    """
    Push already-persisted products into the search index. Runs after
    ingestion commits to PostgreSQL, never in the same transaction/request as
    a user's search — indexing failures never block ingestion and vice versa.
    """
    try:
        run_async(_index_products_async, product_ids)
    except SearchIndexError as exc:
        logger.warning("product_indexing_failed", product_ids=product_ids, error=str(exc))
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error("product_indexing_exhausted_retries", product_ids=product_ids)


async def _index_products_async(product_ids: list[str]) -> None:
    settings = get_settings()
    search_index = OpenSearchIndex(settings)
    try:
        await search_index.ensure_index()
        async with worker_session() as session:
            repo = ProductRepository(session)
            products = await repo.list_by_ids([uuid.UUID(pid) for pid in product_ids])
            documents = [product_to_search_document(p) for p in products]
        await search_index.bulk_index_products(documents)
        logger.info("products_indexed", count=len(documents))
    finally:
        await search_index.close()
