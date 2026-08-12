import uuid

from fastapi.testclient import TestClient

from app.api.deps import get_product_service, get_search_service
from app.core.exceptions import NotFoundError
from app.main import app
from app.schemas.search import ProductSearchResponse
from app.search.base import SearchIndex


class FakeSearchIndex(SearchIndex):
    async def index_product(self, product_id, document):
        raise NotImplementedError

    async def bulk_index_products(self, documents):
        raise NotImplementedError

    async def delete_product(self, product_id):
        raise NotImplementedError

    async def ensure_index(self):
        pass

    async def search(self, query, filters=None, sort="relevance", page=1, page_size=20):
        hit = {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Nike Revolution 7",
            "brand": "Nike",
            "marketplace": "myntra",
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


class FakeProductService:
    def __init__(self, existing_id: uuid.UUID):
        self._existing_id = existing_id

    async def get_product(self, product_id: uuid.UUID):
        if product_id != self._existing_id:
            raise NotFoundError(f"Product {product_id} not found")
        raise NotImplementedError("not needed for this test")


async def _fake_search_service():
    from app.services.search_service import SearchService

    yield SearchService(FakeSearchIndex())


def test_search_products_returns_hits_from_index():
    app.dependency_overrides[get_search_service] = _fake_search_service
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/products/search", params={"q": "nike running shoes"})
    finally:
        app.dependency_overrides.pop(get_search_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["products"][0]["name"] == "Nike Revolution 7"
    assert body["products"][0]["marketplace"] == "myntra"


def test_search_products_requires_query_param():
    with TestClient(app) as client:
        response = client.get("/api/v1/products/search")
    assert response.status_code == 422


def test_get_product_not_found_returns_404():
    existing_id = uuid.uuid4()

    async def _fake_product_service():
        yield FakeProductService(existing_id)

    app.dependency_overrides[get_product_service] = _fake_product_service
    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/products/{uuid.uuid4()}")
    finally:
        app.dependency_overrides.pop(get_product_service, None)

    assert response.status_code == 404
