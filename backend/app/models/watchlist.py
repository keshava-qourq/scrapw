import uuid
from datetime import datetime

from sqlalchemy import Float, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime

from app.db.database import Base


class WatchlistItem(Base):
    """
    A price a user found for a product on some marketplace, entered by hand.
    Not tied to any connector or ingestion job — this is a personal price
    board, not a scraped listing. `group_key` (a normalized `product_name`)
    is what lets otherwise-unrelated entries be compared side by side as
    "the same product" across marketplaces.
    """

    __tablename__ = "watchlist_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    group_key: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    marketplace: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<WatchlistItem id={self.id} product_name={self.product_name!r} marketplace={self.marketplace!r}>"
