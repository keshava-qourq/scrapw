from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.deps import get_live_search_service, get_search_repository
from app.main import app
from app.schemas.live_search import (
    Availability,
    LiveProduct,
    LiveSearchResponse,
    Marketplace,
    ParsedQuery,
)


class FakeLiveSearchService:
    async def search(self, filters):
        product = LiveProduct(
            id="1",
            title="Nike Revolution 7",
            marketplace=Marketplace.AMAZON,
            price=4499,
            rating=4.3,
            product_url="https://example.com/1",
            source="serpapi",
            scraped_at=datetime.now(timezone.utc),
            availability=Availability.UNKNOWN,
        )
        return LiveSearchResponse(
            query=filters.query,
            parsed_query=ParsedQuery(keywords=["nike"]),
            total=1,
            page=filters.page,
            limit=filters.limit,
            results=[product],
            marketplace_status={"serpapi": "success"},
        )


class FailingLiveSearchService:
    async def search(self, filters):
        raise RuntimeError("boom")


class FakeSearchRepository:
    def __init__(self):
        self.recorded = []

    async def record_search(self, query, filters, result_count):
        self.recorded.append((query, filters, result_count))


def test_search_live_returns_results():
    fake_repo = FakeSearchRepository()
    app.dependency_overrides[get_live_search_service] = lambda: FakeLiveSearchService()
    app.dependency_overrides[get_search_repository] = lambda: fake_repo
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/search/live", params={"q": "nike shoes"})
    finally:
        app.dependency_overrides.pop(get_live_search_service, None)
        app.dependency_overrides.pop(get_search_repository, None)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["results"][0]["marketplace"] == "AMAZON"
    assert body["marketplace_status"] == {"serpapi": "success"}
    assert len(fake_repo.recorded) == 1


def test_search_live_requires_query_param():
    with TestClient(app) as client:
        response = client.get("/api/v1/search/live")
    assert response.status_code == 422


def test_search_live_history_write_failure_does_not_fail_request():
    class BrokenSearchRepository:
        async def record_search(self, *args, **kwargs):
            raise RuntimeError("db down")

    app.dependency_overrides[get_live_search_service] = lambda: FakeLiveSearchService()
    app.dependency_overrides[get_search_repository] = lambda: BrokenSearchRepository()
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/search/live", params={"q": "nike shoes"})
    finally:
        app.dependency_overrides.pop(get_live_search_service, None)
        app.dependency_overrides.pop(get_search_repository, None)

    assert response.status_code == 200
