from datetime import date, datetime, timezone

from app.models.card import CardOffer, OfferType
from app.schemas.live_search import Availability, LiveProduct, Marketplace
from app.services.card_offer_service import apply_best_offer, compute_discount, offer_applies_to_product


def _offer(**overrides) -> CardOffer:
    defaults = dict(
        id="offer-1",
        card_id="card-1",
        title="10% off on Amazon",
        offer_type=OfferType.INSTANT_DISCOUNT,
        discount_percentage=10,
        discount_flat_amount=None,
        max_discount_amount=None,
        min_transaction_amount=None,
        eligible_marketplace=None,
        eligible_category=None,
        valid_from=None,
        valid_until=None,
        is_active=True,
    )
    defaults.update(overrides)
    return CardOffer(**defaults)


def _product(price=1000.0, marketplace=Marketplace.AMAZON, category=None) -> LiveProduct:
    return LiveProduct(
        id="p1",
        title="Test product",
        marketplace=marketplace,
        price=price,
        product_url="https://example.com/1",
        source="fake",
        scraped_at=datetime.now(timezone.utc),
        availability=Availability.UNKNOWN,
        category=category,
    )


def test_compute_discount_percentage():
    offer = _offer(discount_percentage=10, discount_flat_amount=None)
    assert compute_discount(offer, 1000.0) == 100.0


def test_compute_discount_flat_capped_at_price():
    offer = _offer(discount_percentage=None, discount_flat_amount=5000)
    assert compute_discount(offer, 1000.0) == 1000.0


def test_compute_discount_percentage_capped_by_max():
    offer = _offer(discount_percentage=50, discount_flat_amount=None, max_discount_amount=100)
    assert compute_discount(offer, 1000.0) == 100.0


def test_offer_inactive_does_not_apply():
    offer = _offer(is_active=False)
    assert offer_applies_to_product(offer, _product(), date.today()) is False


def test_offer_outside_validity_window_does_not_apply():
    offer = _offer(valid_until=date(2020, 1, 1))
    assert offer_applies_to_product(offer, _product(), date(2026, 1, 1)) is False


def test_offer_wrong_marketplace_does_not_apply():
    offer = _offer(eligible_marketplace="FLIPKART")
    assert offer_applies_to_product(offer, _product(marketplace=Marketplace.AMAZON), date.today()) is False


def test_offer_below_min_transaction_does_not_apply():
    offer = _offer(min_transaction_amount=2000)
    assert offer_applies_to_product(offer, _product(price=1000), date.today()) is False


def test_apply_best_offer_picks_highest_discount():
    product = _product(price=1000.0)
    offers = [
        _offer(id="a", title="5% off", discount_percentage=5, discount_flat_amount=None),
        _offer(id="b", title="15% off", discount_percentage=15, discount_flat_amount=None),
    ]
    apply_best_offer(product, offers)

    assert product.applied_offer == "15% off"
    assert product.effective_price == 850.0


def test_apply_best_offer_no_match_leaves_fields_null():
    product = _product(price=1000.0)
    offers = [_offer(eligible_marketplace="FLIPKART")]
    apply_best_offer(product, offers)

    assert product.applied_offer is None
    assert product.effective_price is None
