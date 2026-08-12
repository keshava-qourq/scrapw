import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistGroup, WatchlistItemCreate

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_group_key(product_name: str) -> str:
    return _WHITESPACE_RE.sub(" ", product_name.strip().lower())


class WatchlistService:
    """
    Personal price board: users add prices they found by hand for a product
    across marketplaces, grouped by a normalized product name so they can be
    compared side by side. No connector, no ingestion job — purely
    user-entered data.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_item(self, data: WatchlistItemCreate) -> WatchlistItem:
        item = WatchlistItem(
            product_name=data.product_name.strip(),
            group_key=normalize_group_key(data.product_name),
            marketplace=data.marketplace.strip(),
            price=data.price,
            rating=data.rating,
            url=data.url.strip(),
            notes=data.notes,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item_id: uuid.UUID) -> None:
        item = await self.session.get(WatchlistItem, item_id)
        if item is None:
            raise NotFoundError(f"Watchlist item {item_id} not found")
        await self.session.delete(item)
        await self.session.commit()

    async def list_groups(self) -> list[WatchlistGroup]:
        result = await self.session.execute(
            select(WatchlistItem).order_by(WatchlistItem.group_key, WatchlistItem.price.asc())
        )
        items = list(result.scalars().all())

        groups: dict[str, list[WatchlistItem]] = {}
        for item in items:
            groups.setdefault(item.group_key, []).append(item)

        result_groups: list[WatchlistGroup] = []
        for group_key, group_items in groups.items():
            cheapest = min(group_items, key=lambda i: i.price)
            rated = [i for i in group_items if i.rating is not None]
            best_rated = max(rated, key=lambda i: i.rating) if rated else None
            result_groups.append(
                WatchlistGroup(
                    group_key=group_key,
                    product_name=group_items[0].product_name,
                    items=list(group_items),
                    lowest_price_item_id=cheapest.id,
                    highest_rated_item_id=best_rated.id if best_rated else None,
                )
            )

        result_groups.sort(key=lambda g: min(i.price for i in g.items))
        return result_groups
