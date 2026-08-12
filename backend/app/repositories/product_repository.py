import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        result = await self.session.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_by_marketplace_product_id(
        self, marketplace_id: int, marketplace_product_id: str
    ) -> Product | None:
        result = await self.session.execute(
            select(Product).where(
                Product.marketplace_id == marketplace_id,
                Product.marketplace_product_id == marketplace_product_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(self, product: Product) -> Product:
        """Insert a new product, or update the existing row for the same
        (marketplace, marketplace_product_id) pair."""
        existing = await self.get_by_marketplace_product_id(
            product.marketplace_id, product.marketplace_product_id
        )
        if existing is None:
            self.session.add(product)
            await self.session.flush()
            return product

        for field in (
            "name",
            "brand",
            "category",
            "description",
            "images",
            "price",
            "mrp",
            "discount_percentage",
            "currency",
            "rating",
            "review_count",
            "availability",
            "sizes",
            "colors",
            "seller_name",
            "seller_rating",
            "specifications",
            "raw_data",
            "product_url",
        ):
            setattr(existing, field, getattr(product, field))

        await self.session.flush()
        return existing

    async def list_by_ids(self, product_ids: list[uuid.UUID]) -> list[Product]:
        result = await self.session.execute(select(Product).where(Product.id.in_(product_ids)))
        return list(result.scalars().all())
