from typing import Any

from app.models.product import Product
from app.schemas.search import ProductSearchFilters, ProductSearchResponse
from app.search.base import SearchIndex


def product_to_search_document(product: Product) -> dict[str, Any]:
    """Build the OpenSearch document for a `Product` row. Single source of
    truth for the indexed shape, used by both real-time and batch indexing."""
    return {
        "id": str(product.id),
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "description": product.description,
        "marketplace": product.marketplace.code if product.marketplace else None,
        "price": float(product.price) if product.price is not None else None,
        "mrp": float(product.mrp) if product.mrp is not None else None,
        "discount_percentage": product.discount_percentage,
        "rating": product.rating,
        "review_count": product.review_count,
        "availability": product.availability.value,
        "sizes": product.sizes,
        "colors": product.colors,
        "image_url": product.images[0] if product.images else None,
        "product_url": product.product_url,
        "last_updated_at": product.last_updated_at.isoformat() if product.last_updated_at else None,
    }


class SearchService:
    """
    Read path for product search: FastAPI -> SearchService -> SearchIndex ->
    OpenSearch -> indexed products, returned without ever touching a
    marketplace connector. Ingestion (which populates the index) runs
    entirely separately via background workers.
    """

    def __init__(self, search_index: SearchIndex):
        self.search_index = search_index

    async def search(self, filters: ProductSearchFilters) -> ProductSearchResponse:
        filter_dict = {
            "marketplace": filters.marketplace,
            "brand": filters.brand,
            "category": filters.category,
            "min_price": filters.min_price,
            "max_price": filters.max_price,
            "min_rating": filters.min_rating,
            "min_discount": filters.min_discount,
            "availability": filters.availability,
            "size": filters.size,
            "color": filters.color,
        }
        hits, total = await self.search_index.search(
            query=filters.query,
            filters=filter_dict,
            sort=filters.sort.value,
            page=filters.page,
            page_size=filters.page_size,
        )
        return ProductSearchResponse(
            query=filters.query,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            products=hits,
        )
