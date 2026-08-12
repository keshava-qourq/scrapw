import pytest

from app.schemas.search import ProductSearchFilters, SortOption
from app.search.base import SearchIndex
from app.services.search_service import SearchService


class FakeSearchIndex(SearchIndex):
    def __init__(self):
        self.last_query = None
        self.last_filters = None
        self.last_sort = None

    async def index_product(self, product_id, document):
        raise NotImplementedError

    async def bulk_index_products(self, documents):
        raise NotImplementedError

    async def delete_product(self, product_id):
        raise NotImplementedError

    async def ensure_index(self):
        raise NotImplementedError

    async def search(self, query, filters=None, sort="relevance", page=1, page_size=20):
        self.last_query = query
        self.last_filters = filters
        self.last_sort = sort
        return (
            [
                {
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
            ],
            1,
        )


@pytest.mark.asyncio
async def test_search_passes_filters_through_to_index():
    fake_index = FakeSearchIndex()
    service = SearchService(fake_index)

    filters = ProductSearchFilters(
        query="nike running shoes",
        brand="Nike",
        min_price=1000,
        max_price=6000,
        sort=SortOption.PRICE_LOW_TO_HIGH,
    )
    response = await service.search(filters)

    assert fake_index.last_query == "nike running shoes"
    assert fake_index.last_filters["brand"] == "Nike"
    assert fake_index.last_filters["min_price"] == 1000
    assert fake_index.last_sort == "price_low_to_high"
    assert response.total == 1
    assert response.products[0].name == "Nike Revolution 7"
