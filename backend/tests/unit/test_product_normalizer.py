from app.schemas.live_search import Marketplace
from app.services.product_normalizer import normalize_serpapi_shopping_result


def test_normalizes_full_serpapi_result():
    item = {
        "title": "Nike Revolution 7 Running Shoes",
        "product_link": "https://www.amazon.in/dp/B0ABC123",
        "source": "Amazon.in",
        "extracted_price": 4499.0,
        "extracted_original_price": 5995.0,
        "rating": 4.3,
        "reviews": 8213,
        "thumbnail": "https://example.com/img.jpg",
        "product_id": "B0ABC123",
    }
    product = normalize_serpapi_shopping_result(item)

    assert product is not None
    assert product.title == "Nike Revolution 7 Running Shoes"
    assert product.marketplace == Marketplace.AMAZON
    assert product.price == 4499.0
    assert product.original_price == 5995.0
    assert product.discount_percentage == 24.95
    assert product.rating == 4.3
    assert product.review_count == 8213
    assert product.source == "serpapi"


def test_missing_title_or_link_returns_none():
    assert normalize_serpapi_shopping_result({"product_link": "https://x.com"}) is None
    assert normalize_serpapi_shopping_result({"title": "Shoes"}) is None


def test_missing_optional_fields_stay_null_not_fabricated():
    item = {
        "title": "Some Product",
        "link": "https://unknown-store.example.com/p/1",
    }
    product = normalize_serpapi_shopping_result(item)

    assert product is not None
    assert product.price is None
    assert product.rating is None
    assert product.review_count is None
    assert product.seller is None
    assert product.marketplace == Marketplace.OTHER


def test_discount_percentage_not_computed_without_original_price():
    item = {
        "title": "Some Product",
        "link": "https://example.com/p/1",
        "extracted_price": 100.0,
    }
    product = normalize_serpapi_shopping_result(item)

    assert product.discount_percentage is None
