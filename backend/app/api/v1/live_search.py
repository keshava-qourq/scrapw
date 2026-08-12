import time
import uuid

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_card_offer_service, get_live_search_service, get_search_repository
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.rate_limit import limiter
from app.repositories.search_repository import SearchRepository
from app.schemas.live_search import LiveSearchFilters, LiveSearchResponse, LiveSortOption, Marketplace
from app.services.card_offer_service import CardOfferService, apply_best_offer
from app.services.live_search_service import LiveSearchService

router = APIRouter(prefix="/search", tags=["live-search"])
logger = get_logger(__name__)


@router.get(
    "/live",
    response_model=LiveSearchResponse,
    summary="Live cross-marketplace search",
    description=(
        "Searches Amazon, Flipkart, Myntra, and AJIO in real time via SerpApi, with Gemini "
        "turning the free-text query into structured search intent first. Results are "
        "deduplicated, filtered, sorted, and cached (default 15 min TTL). Returns "
        "`marketplace_status` per provider so a single provider outage never fails the whole "
        "search — see the `unavailable` status for providers that couldn't be reached. Pass "
        "`card_id` to also compute an `effective_price`/`applied_offer` per result from that "
        "card's manually-entered offers (see `/cards`) — this never affects caching, since "
        "offers are applied per-request, after the (offer-agnostic) cached result is fetched."
    ),
)
@limiter.limit(lambda: get_settings().search_rate_limit)
async def search_live(
    request: Request,
    q: str,
    page: int = 1,
    limit: int = 20,
    marketplace: Marketplace | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    sort: LiveSortOption = LiveSortOption.RELEVANCE,
    card_id: uuid.UUID | None = None,
    service: LiveSearchService = Depends(get_live_search_service),
    search_repository: SearchRepository = Depends(get_search_repository),
    card_offer_service: CardOfferService = Depends(get_card_offer_service),
) -> LiveSearchResponse:
    filters = LiveSearchFilters(
        query=q,
        marketplace=marketplace,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort=sort,
        page=page,
        limit=limit,
    )

    started = time.monotonic()
    response = await service.search(filters)

    if card_id is not None:
        offers = await card_offer_service.list_offers(card_id)
        for product in response.results:
            apply_best_offer(product, offers)

    duration_ms = round((time.monotonic() - started) * 1000, 1)

    logger.info(
        "live_search_completed",
        query=q,
        result_count=response.total,
        cache_hit=response.cache_hit,
        duration_ms=duration_ms,
        marketplace_status=response.marketplace_status,
    )

    try:
        await search_repository.record_search(
            query=q,
            filters=filters.model_dump(mode="json", exclude={"query"}),
            result_count=response.total,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("search_history_write_failed", error=str(exc))

    return response
