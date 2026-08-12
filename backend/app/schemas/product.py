import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.product import AvailabilityStatus


class ProductBase(BaseModel):
    marketplace_product_id: str
    product_url: str
    name: str
    brand: str | None = None
    category: str | None = None
    description: str | None = None
    images: list[str] = Field(default_factory=list)
    price: float | None = None
    mrp: float | None = None
    discount_percentage: float | None = None
    currency: str = "INR"
    rating: float | None = None
    review_count: int | None = None
    availability: AvailabilityStatus = AvailabilityStatus.UNKNOWN
    sizes: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    seller_name: str | None = None
    seller_rating: float | None = None
    specifications: dict = Field(default_factory=dict)


class ProductCreate(ProductBase):
    marketplace_code: str
    raw_data: dict = Field(default_factory=dict)


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    marketplace: str
    canonical_product_id: uuid.UUID | None = None
    first_seen_at: datetime
    last_updated_at: datetime


class ProductSearchResult(BaseModel):
    """Slim representation returned by the search API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    brand: str | None = None
    marketplace: str
    price: float | None = None
    mrp: float | None = None
    discount_percentage: float | None = None
    rating: float | None = None
    review_count: int | None = None
    image_url: str | None = None
    product_url: str
    availability: AvailabilityStatus = AvailabilityStatus.UNKNOWN
