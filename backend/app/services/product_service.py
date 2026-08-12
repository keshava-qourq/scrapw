import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.product import Product
from app.repositories.marketplace_repository import MarketplaceRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate
from app.services.deduplication_service import DeduplicationService


class ProductService:
    """
    Owns the persistence side of the ingestion pipeline: given a validated
    `ProductCreate` from the normalization stage, resolve its marketplace,
    upsert the product row, and assign it to a canonical product group.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.products = ProductRepository(session)
        self.marketplaces = MarketplaceRepository(session)
        self.dedup = DeduplicationService(session)

    async def get_product(self, product_id: uuid.UUID) -> Product:
        product = await self.products.get_by_id(product_id)
        if product is None:
            raise NotFoundError(f"Product {product_id} not found")
        return product

    async def ingest_product(self, data: ProductCreate, marketplace_name: str | None = None) -> Product:
        marketplace = await self.marketplaces.get_or_create(
            code=data.marketplace_code,
            name=marketplace_name or data.marketplace_code.title(),
        )

        product = Product(
            marketplace_id=marketplace.id,
            marketplace_product_id=data.marketplace_product_id,
            product_url=data.product_url,
            name=data.name,
            brand=data.brand,
            category=data.category,
            description=data.description,
            images=data.images,
            price=data.price,
            mrp=data.mrp,
            discount_percentage=data.discount_percentage,
            currency=data.currency,
            rating=data.rating,
            review_count=data.review_count,
            availability=data.availability,
            sizes=data.sizes,
            colors=data.colors,
            seller_name=data.seller_name,
            seller_rating=data.seller_rating,
            specifications=data.specifications,
            raw_data=data.raw_data,
        )

        saved = await self.products.upsert(product)
        await self.dedup.assign_canonical_product(saved)
        await self.session.commit()
        return saved
