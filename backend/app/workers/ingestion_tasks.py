from typing import Any

from celery import shared_task

from app.connectors.registry import build_connector
from app.core.config import get_settings
from app.core.exceptions import MarketplaceError, ValidationError
from app.core.logging import get_logger
from app.services.deduplication_service import DeduplicationService
from app.services.normalization_service import NormalizationService
from app.services.product_service import ProductService
from app.workers.indexing_tasks import index_products
from app.workers.utils import run_async, worker_session

logger = get_logger(__name__)

# Seed queries used to exercise ingestion end-to-end without a real search
# term coming from a user. Real deployments would replace/extend this with a
# catalog crawl plan or an affiliate feed's category list.
_SEED_QUERIES = ["nike running shoes", "sneakers"]


@shared_task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def fetch_marketplace_products(self, marketplace_code: str, query: str) -> list[str]:
    """
    Fetch + parse + validate + normalize + deduplicate + store products for a
    single marketplace/query, independently of every other marketplace.
    A failure here (e.g. a marketplace timeout) retries with backoff and,
    once retries are exhausted, is logged and swallowed rather than
    propagated — it must never take down other marketplaces' jobs.
    """
    try:
        return run_async(_fetch_marketplace_products_async, marketplace_code, query)
    except MarketplaceError as exc:
        logger.warning("marketplace_fetch_failed", marketplace=marketplace_code, query=query, error=str(exc))
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error("marketplace_fetch_exhausted_retries", marketplace=marketplace_code, query=query)
            return []


async def _fetch_marketplace_products_async(marketplace_code: str, query: str) -> list[str]:
    settings = get_settings()
    connector = build_connector(marketplace_code, settings)
    product_ids: list[str] = []
    try:
        raw_products = await connector.search_products(query)
        async with worker_session() as session:
            service = ProductService(session)
            for raw_product in raw_products:
                try:
                    mapped = connector.normalize_product(raw_product)
                    validated = NormalizationService.normalize(mapped)
                except ValidationError as exc:
                    logger.warning(
                        "product_normalization_failed",
                        marketplace=marketplace_code,
                        marketplace_product_id=raw_product.marketplace_product_id,
                        error=str(exc),
                    )
                    continue
                product = await service.ingest_product(validated)
                product_ids.append(str(product.id))
    finally:
        await connector.aclose()

    if product_ids:
        index_products.delay(product_ids)
    return product_ids


@shared_task(bind=True, max_retries=3, retry_backoff=True, retry_backoff_max=60, retry_jitter=True)
def update_product(self, marketplace_code: str, product_url: str) -> str | None:
    """Refresh a single already-known product from its marketplace source."""
    try:
        return run_async(_update_product_async, marketplace_code, product_url)
    except MarketplaceError as exc:
        logger.warning("product_update_failed", marketplace=marketplace_code, url=product_url, error=str(exc))
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error("product_update_exhausted_retries", marketplace=marketplace_code, url=product_url)
            return None


async def _update_product_async(marketplace_code: str, product_url: str) -> str | None:
    settings = get_settings()
    connector = build_connector(marketplace_code, settings)
    try:
        raw_product = await connector.fetch_product(product_url)
        if raw_product is None:
            return None
        mapped = connector.normalize_product(raw_product)
        validated = NormalizationService.normalize(mapped)
        async with worker_session() as session:
            product = await ProductService(session).ingest_product(validated)
        index_products.delay([str(product.id)])
        return str(product.id)
    finally:
        await connector.aclose()


@shared_task
def normalize_product(raw_product: dict[str, Any]) -> dict[str, Any]:
    """Standalone task wrapping NormalizationService, usable for
    reprocessing/backfills independently of a live connector fetch."""
    validated = NormalizationService.normalize(raw_product)
    return validated.model_dump(mode="json")


@shared_task
def deduplicate_products(product_ids: list[str]) -> None:
    """Re-run canonical-product assignment for an already-stored batch of
    products, e.g. after a change to the matching strategy."""
    run_async(_deduplicate_products_async, product_ids)


async def _deduplicate_products_async(product_ids: list[str]) -> None:
    import uuid

    async with worker_session() as session:
        service = ProductService(session)
        dedup = DeduplicationService(session)
        for product_id in product_ids:
            product = await service.products.get_by_id(uuid.UUID(product_id))
            if product is not None:
                await dedup.assign_canonical_product(product)
        await session.commit()


@shared_task
def refresh_marketplace(marketplace_code: str) -> None:
    """
    Scheduled entry point (see celery_app.beat_schedule): fan out one
    `fetch_marketplace_products` task per seed query for this marketplace.
    Runs entirely independently of every other marketplace's refresh job.
    """
    logger.info("refresh_marketplace_started", marketplace=marketplace_code)
    for query in _SEED_QUERIES:
        fetch_marketplace_products.delay(marketplace_code, query)
