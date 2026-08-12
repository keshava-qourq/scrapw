import enum

from pydantic import BaseModel, Field

from app.schemas.product import ProductSearchResult


class SortOption(str, enum.Enum):
    RELEVANCE = "relevance"
    PRICE_LOW_TO_HIGH = "price_low_to_high"
    PRICE_HIGH_TO_LOW = "price_high_to_low"
    RATING = "rating"
    DISCOUNT = "discount"
    NEWEST = "newest"


class ProductSearchFilters(BaseModel):
    query: str = Field(..., min_length=1)
    marketplace: str | None = None
    brand: str | None = None
    category: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_rating: float | None = None
    min_discount: float | None = None
    availability: str | None = None
    size: str | None = None
    color: str | None = None
    sort: SortOption = SortOption.RELEVANCE
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class ProductSearchResponse(BaseModel):
    query: str
    total: int
    page: int
    page_size: int
    products: list[ProductSearchResult]
