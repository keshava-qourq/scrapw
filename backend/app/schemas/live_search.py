import enum
from datetime import datetime

from pydantic import BaseModel, Field


class Marketplace(str, enum.Enum):
    AMAZON = "AMAZON"
    FLIPKART = "FLIPKART"
    MYNTRA = "MYNTRA"
    AJIO = "AJIO"
    OTHER = "OTHER"


class Availability(str, enum.Enum):
    IN_STOCK = "IN_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    UNKNOWN = "UNKNOWN"


class LiveSortOption(str, enum.Enum):
    RELEVANCE = "relevance"
    PRICE_LOW_TO_HIGH = "price_low_to_high"
    PRICE_HIGH_TO_LOW = "price_high_to_low"
    RATING = "rating"
    DISCOUNT = "discount"


class LiveProduct(BaseModel):
    """
    A single product result from a provider, already mapped onto the common
    shape. Every field the provider didn't actually return stays null —
    nothing here is invented to fill gaps.
    """

    id: str
    title: str
    brand: str | None = None
    marketplace: Marketplace
    seller: str | None = None
    price: float | None = None
    original_price: float | None = None
    discount_percentage: float | None = None
    currency: str = "INR"
    rating: float | None = None
    review_count: int | None = None
    image_url: str | None = None
    product_url: str
    availability: Availability = Availability.UNKNOWN
    category: str | None = None
    source: str
    scraped_at: datetime

    duplicate_group: str | None = None
    duplicate_confidence: float | None = None

    # Populated only when a `card_id` is passed to the search and a matching
    # offer exists for this product. Never invented — null unless a real,
    # manually-entered offer actually applies.
    effective_price: float | None = None
    applied_offer: str | None = None


class LiveSearchFilters(BaseModel):
    query: str = Field(..., min_length=1)
    marketplace: Marketplace | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_rating: float | None = None
    sort: LiveSortOption = LiveSortOption.RELEVANCE
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class ParsedQuery(BaseModel):
    """Structured intent extracted from a natural-language query via Gemini
    (or the keyword fallback if Gemini is unavailable/unset)."""

    keywords: list[str] = Field(default_factory=list)
    brand: str | None = None
    category: str | None = None
    max_price: float | None = None
    min_price: float | None = None


class LiveSearchResponse(BaseModel):
    query: str
    parsed_query: ParsedQuery
    total: int
    page: int
    limit: int
    results: list[LiveProduct]
    marketplace_status: dict[str, str]
    cache_hit: bool = False
