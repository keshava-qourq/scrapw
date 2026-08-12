from datetime import datetime, timezone

from app.schemas.live_search import Availability, LiveProduct, Marketplace
from app.services.live_deduplication_service import deduplicate_live_products


def _product(title: str, brand: str, marketplace: Marketplace, product_id: str) -> LiveProduct:
    return LiveProduct(
        id=product_id,
        title=title,
        brand=brand,
        marketplace=marketplace,
        product_url=f"https://example.com/{product_id}",
        source="serpapi",
        scraped_at=datetime.now(timezone.utc),
        availability=Availability.UNKNOWN,
    )


def test_same_product_across_marketplaces_grouped():
    products = [
        _product("Samsung 55 inch 4K Smart TV", "Samsung", Marketplace.AMAZON, "1"),
        _product("Samsung 55 Inch 4K Smart TV", "Samsung", Marketplace.FLIPKART, "2"),
    ]
    result = deduplicate_live_products(products)

    assert result[0].duplicate_group is not None
    assert result[0].duplicate_group == result[1].duplicate_group
    assert result[0].duplicate_confidence == 0.94


def test_unrelated_products_not_merged():
    products = [
        _product("Samsung 55 inch 4K Smart TV", "Samsung", Marketplace.AMAZON, "1"),
        _product("Nike Revolution 7 Running Shoes", "Nike", Marketplace.FLIPKART, "2"),
    ]
    result = deduplicate_live_products(products)

    assert result[0].duplicate_group is None
    assert result[1].duplicate_group is None


def test_singleton_not_marked_as_duplicate():
    products = [_product("Unique Product", "BrandX", Marketplace.OTHER, "1")]
    result = deduplicate_live_products(products)

    assert result[0].duplicate_group is None
    assert result[0].duplicate_confidence is None
