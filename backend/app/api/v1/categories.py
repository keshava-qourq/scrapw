from fastapi import APIRouter, Depends
from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.product import Product

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
async def list_categories(session: AsyncSession = Depends(get_db)) -> list[str]:
    result = await session.execute(
        select(distinct(Product.category)).where(Product.category.is_not(None)).order_by(Product.category)
    )
    return [row[0] for row in result.all()]
