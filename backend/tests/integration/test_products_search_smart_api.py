from fastapi.testclient import TestClient

from app.api.deps import get_query_understanding_service, get_search_service
from app.main import app
from app.schemas.search import ProductSearchFilters, SortOption
from app.search.base import SearchIndex


class FakeSearchIndex(SearchIndex):
    def __init__(self):
        self.last_filters = None
        self.last_sort = None

    async def index_product(self, product_id, document):
        raise NotImplementedError

    async def bulk_index_products(self, documents):
        raise NotImplementedError

    async def delete_product(self, product_id):
        raise NotImplementedError

    async def ensure_index(self):
        pass

    async def search(self, query, filters=None, sort="relevance", page=1, page_size=20):
        self.last_filters = filters
        self.last_sort = sort
        hit = {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Nike Revolution 7",
            "brand": "Nike",
            "marketplace": "amazon",
            "price": 4299,
            "mrp": 5995,
            "discount_percentage": 28,
            "rating": 4.4,
            "review_count": 1200,
            "image_url": "https://example.com/img.jpg",
            "product_url": "https://example.com/p/1",
            "availability": "in_stock",
        }
        return [hit], 1


class FakeQueryUnderstandingService:
    async def parse(self, raw_query, *, page=1, page_size=20):
        return ProductSearchFilters(
            query="nike running shoes",
            brand="Nike",
            max_price=5000,
            sort=SortOption.PRICE_LOW_TO_HIGH,
            page=page,
            page_size=page_size,
        )


def test_search_smart_uses_parsed_filters():
    fake_index = FakeSearchIndex()

    async def _fake_search_service():
        from app.services.search_service import SearchService

        yield SearchService(fake_index)

    app.dependency_overrides[get_search_service] = _fake_search_service
    app.dependency_overrides[get_query_understanding_service] = lambda: FakeQueryUnderstandingService()
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/products/search/smart",
                params={"q": "cheap nike running shoes under 5000"},
            )
    finally:
        app.dependency_overrides.pop(get_search_service, None)
        app.dependency_overrides.pop(get_query_understanding_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "nike running shoes"
    assert body["total"] == 1
    assert fake_index.last_filters["brand"] == "Nike"
    assert fake_index.last_filters["max_price"] == 5000
    assert fake_index.last_sort == "price_low_to_high"


def test_search_smart_requires_query_param():
    with TestClient(app) as client:
        response = client.get("/api/v1/products/search/smart")
    assert response.status_code == 422
