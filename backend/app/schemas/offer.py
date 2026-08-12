import enum

from pydantic import BaseModel


class OfferType(str, enum.Enum):
    """Placeholder taxonomy for the future offers feature set (bank/card
    offers, coupons, cashback, EMI, exchange). Not populated yet — this
    exists so `/products/{id}/offers` has a stable response shape to extend."""

    BANK_OFFER = "bank_offer"
    CARD_OFFER = "card_offer"
    COUPON = "coupon"
    CASHBACK = "cashback"
    EMI = "emi"
    EXCHANGE = "exchange"


class Offer(BaseModel):
    type: OfferType
    description: str
    discount_amount: float | None = None
    discount_percentage: float | None = None
    min_transaction_amount: float | None = None
    valid_until: str | None = None
