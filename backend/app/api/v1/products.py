import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_product_service, get_query_understanding_service, get_search_service
from app.core.exceptions import NotFoundError
from app.models.product import AvailabilityStatus
from app.schemas.offer import Offer
from app.schemas.product import ProductRead
from app.schemas.search import ProductSearchFilters, ProductSearchResponse, SortOption
from app.services.product_service import ProductService
from app.services.query_understanding_service import QueryUnderstandingService
from app.services.search_service import SearchService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/search", response_model=ProductSearchResponse)
async def search_products(
    q: str = Query(..., min_length=1, alias="q", description="Search query, e.g. 'nike running shoes'"),
    marketplace: str | None = None,
    brand: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    min_discount: float | None = None,
    availability: AvailabilityStatus | None = None,
    size: str | None = None,
    color: str | None = None,
    sort: SortOption = SortOption.RELEVANCE,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service),
) -> ProductSearchResponse:
    filters = ProductSearchFilters(
        query=q,
        marketplace=marketplace,
        brand=brand,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        min_discount=min_discount,
        availability=availability.value if availability else None,
        size=size,
        color=color,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    return await search_service.search(filters)


@router.get("/search/smart", response_model=ProductSearchResponse)
async def search_products_smart(
    q: str = Query(
        ...,
        min_length=1,
        description="Natural-language query, e.g. 'cheap nike shoes under 5000 with good reviews'",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query_understanding: QueryUnderstandingService = Depends(get_query_understanding_service),
    search_service: SearchService = Depends(get_search_service),
) -> ProductSearchResponse:
    """
    Same read path as `/search`, but the filters are derived from free text via
    Gemini instead of being passed explicitly. Falls back to a plain-text
    search with no extra filters if Gemini is unavailable or misconfigured.
    """
    filters = await query_understanding.parse(q, page=page, page_size=page_size)
    return await search_service.search(filters)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: uuid.UUID,
    product_service: ProductService = Depends(get_product_service),
) -> ProductRead:
    try:
        product = await product_service.get_product(product_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProductRead(
        id=product.id,
        marketplace=product.marketplace.code,
        marketplace_product_id=product.marketplace_product_id,
        product_url=product.product_url,
        canonical_product_id=product.canonical_product_id,
        name=product.name,
        brand=product.brand,
        category=product.category,
        description=product.description,
        images=product.images,
        price=product.price,
        mrp=product.mrp,
        discount_percentage=product.discount_percentage,
        currency=product.currency,
        rating=product.rating,
        review_count=product.review_count,
        availability=product.availability,
        sizes=product.sizes,
        colors=product.colors,
        seller_name=product.seller_name,
        seller_rating=product.seller_rating,
        specifications=product.specifications,
        first_seen_at=product.first_seen_at,
        last_updated_at=product.last_updated_at,
    )


@router.get("/{product_id}/offers", response_model=list[Offer])
async def get_product_offers(
    product_id: uuid.UUID,
    product_service: ProductService = Depends(get_product_service),
) -> list[Offer]:
    """
    Placeholder for the future bank/card offers, coupons, cashback, EMI and
    exchange-offer feature set. Returns an empty list today; the response
    shape (`Offer`) is stable so a real offers service can populate it later
    without an API-breaking change.
    """
    try:
        await product_service.get_product(product_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return []
