import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum

from app.db.database import Base


class CardType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class OfferType(str, enum.Enum):
    INSTANT_DISCOUNT = "instant_discount"
    CASHBACK = "cashback"
    NO_COST_EMI = "no_cost_emi"
    COUPON = "coupon"


class Card(Base):
    """A bank card a user can search offers for. Manually entered — there's
    no public API for this, banks don't expose it."""

    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    card_name: Mapped[str] = mapped_column(String(200), nullable=False)
    card_type: Mapped[CardType] = mapped_column(
        Enum(CardType, name="card_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=CardType.CREDIT,
    )
    network: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    offers = relationship("CardOffer", back_populates="card", lazy="noload", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Card id={self.id} bank_name={self.bank_name!r} card_name={self.card_name!r}>"


class CardOffer(Base):
    """
    One offer available on a card. Discount is either a flat amount or a
    percentage (with an optional cap) — never both at once, enforced at the
    schema level, not here.
    """

    __tablename__ = "card_offers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    offer_type: Mapped[OfferType] = mapped_column(
        Enum(OfferType, name="offer_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    discount_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    discount_flat_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_discount_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_transaction_amount: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Null = applies to any marketplace / any category.
    eligible_marketplace: Mapped[str | None] = mapped_column(String(20), nullable=True)
    eligible_category: Mapped[str | None] = mapped_column(String(200), nullable=True)

    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    card = relationship("Card", back_populates="offers", lazy="joined")

    def __repr__(self) -> str:
        return f"<CardOffer id={self.id} title={self.title!r} card_id={self.card_id}>"
