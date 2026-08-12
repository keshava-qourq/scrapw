from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_history import SearchHistory


class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_search(self, query: str, filters: dict, result_count: int) -> None:
        self.session.add(SearchHistory(query=query, filters=filters, result_count=result_count))
        await self.session.commit()
