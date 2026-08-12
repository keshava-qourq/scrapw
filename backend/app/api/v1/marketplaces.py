from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.repositories.marketplace_repository import MarketplaceRepository

router = APIRouter(prefix="/marketplaces", tags=["marketplaces"])


@router.get("")
async def list_marketplaces(session: AsyncSession = Depends(get_db)) -> list[dict]:
    repo = MarketplaceRepository(session)
    marketplaces = await repo.list_all()
    return [
        {"code": m.code, "name": m.name, "is_active": m.is_active}
        for m in marketplaces
    ]
