import pytest

from app.core.exceptions import ValidationError
from app.models.product import AvailabilityStatus
from app.services.normalization_service import NormalizationService


def _raw(**overrides):
    base = {
        "marketplace_code": "amazon",
        "marketplace_product_id": "ABC123",
        "product_url": "https://example.com/p/ABC123",
        "name": "  Nike   Revolution 7   ",
        "brand": "  Nike ",
        "category": "Footwear",
        "description": "desc",
        "images": ["https://example.com/img.jpg", ""],
        "price": 4299.0,
        "mrp": 5995.0,
        "discount_percentage": None,
        "currency": "INR",
        "rating": 4.4,
        "review_count": 1200,
        "availability": AvailabilityStatus.IN_STOCK,
        "sizes": ["UK8", ""],
        "colors": ["Black", None],
        "seller_name": "Nike",
        "seller_rating": None,
        "specifications": {},
        "raw_data": {},
    }
    base.update(overrides)
    return base


def test_normalize_collapses_whitespace_and_strips_brand():
    result = NormalizationService.normalize(_raw())
    assert result.name == "Nike Revolution 7"
    assert result.brand == "Nike"


def test_normalize_drops_empty_list_entries():
    result = NormalizationService.normalize(_raw())
    assert result.images == ["https://example.com/img.jpg"]
    assert result.sizes == ["UK8"]
    assert result.colors == ["Black"]


def test_normalize_computes_discount_percentage_when_missing():
    result = NormalizationService.normalize(_raw(discount_percentage=None, price=4500.0, mrp=6000.0))
    assert result.discount_percentage == pytest.approx(25.0)


def test_normalize_keeps_explicit_discount_percentage():
    result = NormalizationService.normalize(_raw(discount_percentage=10.0, price=4500.0, mrp=6000.0))
    assert result.discount_percentage == 10.0


def test_normalize_rejects_negative_price():
    with pytest.raises(ValidationError):
        NormalizationService.normalize(_raw(price=-1.0))


def test_normalize_rejects_negative_mrp():
    with pytest.raises(ValidationError):
        NormalizationService.normalize(_raw(mrp=-1.0))


@pytest.mark.parametrize(
    "price,mrp,expected",
    [
        (4500.0, 6000.0, 25.0),
        (6000.0, 6000.0, 0.0),
        (7000.0, 6000.0, 0.0),  # price above mrp should clamp to 0, not go negative
        (100.0, 0.0, None),
    ],
)
def test_calculate_discount(price, mrp, expected):
    assert NormalizationService.calculate_discount(price, mrp) == expected
