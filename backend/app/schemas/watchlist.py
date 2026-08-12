import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WatchlistItemCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=500)
    marketplace: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    rating: float | None = Field(None, ge=0, le=5)
    url: str = Field(..., min_length=1)
    notes: str | None = None


class WatchlistItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_name: str
    group_key: str
    marketplace: str
    price: float
    rating: float | None
    url: str
    notes: str | None
    created_at: datetime


class WatchlistGroup(BaseModel):
    group_key: str
    product_name: str
    items: list[WatchlistItemRead]
    lowest_price_item_id: uuid.UUID | None
    highest_rated_item_id: uuid.UUID | None
