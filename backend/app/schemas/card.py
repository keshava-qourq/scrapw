import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.card import CardType, OfferType


class CardCreate(BaseModel):
    bank_name: str = Field(..., min_length=1, max_length=100)
    card_name: str = Field(..., min_length=1, max_length=200)
    card_type: CardType = CardType.CREDIT
    network: str | None = None


class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    bank_name: str
    card_name: str
    card_type: CardType
    network: str | None
    created_at: datetime


class CardOfferCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    offer_type: OfferType
    discount_percentage: float | None = Field(None, ge=0, le=100)
    discount_flat_amount: float | None = Field(None, ge=0)
    max_discount_amount: float | None = Field(None, ge=0)
    min_transaction_amount: float | None = Field(None, ge=0)
    eligible_marketplace: str | None = None
    eligible_category: str | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    terms: str | None = None
    is_active: bool = True

    @model_validator(mode="after")
    def _exactly_one_discount_kind(self) -> "CardOfferCreate":
        has_percentage = self.discount_percentage is not None
        has_flat = self.discount_flat_amount is not None
        if has_percentage == has_flat:
            raise ValueError("Set exactly one of discount_percentage or discount_flat_amount")
        return self


class CardOfferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    card_id: uuid.UUID
    title: str
    offer_type: OfferType
    discount_percentage: float | None
    discount_flat_amount: float | None
    max_discount_amount: float | None
    min_transaction_amount: float | None
    eligible_marketplace: str | None
    eligible_category: str | None
    valid_from: date | None
    valid_until: date | None
    terms: str | None
    is_active: bool
    created_at: datetime
