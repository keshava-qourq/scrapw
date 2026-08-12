from celery import Celery
from celery.schedules import crontab

from app.connectors.registry import SUPPORTED_MARKETPLACES
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "product_search_engine",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.ingestion_tasks", "app.workers.indexing_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=30,
    task_time_limit=300,
    task_soft_time_limit=240,
)

# Stagger each marketplace's refresh job so they never fire at the exact same
# moment and compete for the same worker pool / rate-limit budget.
celery_app.conf.beat_schedule = {
    f"refresh-{marketplace}": {
        "task": "app.workers.ingestion_tasks.refresh_marketplace",
        "schedule": crontab(minute=str(minute_offset * 15)),
        "args": (marketplace,),
    }
    for minute_offset, marketplace in enumerate(SUPPORTED_MARKETPLACES)
}
