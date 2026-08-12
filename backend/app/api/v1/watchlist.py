import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.watchlist import WatchlistGroup, WatchlistItemCreate, WatchlistItemRead
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


async def get_watchlist_service(session: AsyncSession = Depends(get_db)) -> AsyncGenerator[WatchlistService, None]:
    yield WatchlistService(session)


@router.post("", response_model=WatchlistItemRead, status_code=201)
async def add_watchlist_item(
    data: WatchlistItemCreate,
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistItemRead:
    return await service.add_item(data)


@router.get("/groups", response_model=list[WatchlistGroup])
async def list_watchlist_groups(
    service: WatchlistService = Depends(get_watchlist_service),
) -> list[WatchlistGroup]:
    return await service.list_groups()


@router.delete("/{item_id}", status_code=204)
async def delete_watchlist_item(
    item_id: uuid.UUID,
    service: WatchlistService = Depends(get_watchlist_service),
) -> None:
    await service.delete_item(item_id)
