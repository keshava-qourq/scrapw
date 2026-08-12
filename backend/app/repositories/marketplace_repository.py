from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.marketplace import Marketplace


class MarketplaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_code(self, code: str) -> Marketplace | None:
        result = await self.session.execute(select(Marketplace).where(Marketplace.code == code))
        return result.scalar_one_or_none()

    async def list_all(self, active_only: bool = False) -> list[Marketplace]:
        query = select(Marketplace)
        if active_only:
            query = query.where(Marketplace.is_active.is_(True))
        result = await self.session.execute(query.order_by(Marketplace.name))
        return list(result.scalars().all())

    async def get_or_create(self, code: str, name: str, base_url: str = "") -> Marketplace:
        marketplace = await self.get_by_code(code)
        if marketplace:
            return marketplace
        marketplace = Marketplace(code=code, name=name, base_url=base_url)
        self.session.add(marketplace)
        await self.session.flush()
        return marketplace
