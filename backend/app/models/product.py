import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Enum, Float

from app.db.database import Base


class AvailabilityStatus(str, enum.Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    LIMITED_STOCK = "limited_stock"
    UNKNOWN = "unknown"


class CanonicalProduct(Base):
    """
    Represents a single real-world product that may be sold across multiple
    marketplaces. Used to group `Product` rows for cross-marketplace comparison.

    Populated by the deduplication service; safe to leave unset (nullable FK on
    Product) until a match is found.
    """

    __tablename__ = "canonical_products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str | None] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    products = relationship("Product", back_populates="canonical_product", lazy="noload")


class Product(Base):
    """Normalized product listing as sold by one marketplace."""

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("marketplace_id", "marketplace_product_id", name="uq_marketplace_product"),
        Index("ix_products_brand_category", "brand", "category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    marketplace_id: Mapped[int] = mapped_column(ForeignKey("marketplaces.id"), nullable=False)
    marketplace_product_id: Mapped[str] = mapped_column(String(255), nullable=False)
    product_url: Mapped[str] = mapped_column(Text, nullable=False)

    canonical_product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("canonical_products.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    images: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)

    price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    mrp: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    discount_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")

    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    availability: Mapped[AvailabilityStatus] = mapped_column(
        Enum(
            AvailabilityStatus,
            name="availability_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=AvailabilityStatus.UNKNOWN,
    )

    sizes: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    colors: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)

    seller_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seller_rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    specifications: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    marketplace = relationship("Marketplace", back_populates="products", lazy="joined")
    canonical_product = relationship("CanonicalProduct", back_populates="products", lazy="noload")

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r} marketplace_id={self.marketplace_id}>"
