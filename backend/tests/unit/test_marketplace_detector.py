from app.schemas.live_search import Marketplace
from app.services.marketplace_detector import detect_marketplace


def test_detects_amazon_from_url():
    assert detect_marketplace(url="https://www.amazon.in/dp/B0ABC123") == Marketplace.AMAZON


def test_detects_flipkart_from_source_name():
    assert detect_marketplace(source_name="Flipkart.com") == Marketplace.FLIPKART


def test_detects_myntra_case_insensitive():
    assert detect_marketplace(source_name="MYNTRA") == Marketplace.MYNTRA


def test_detects_ajio_from_url():
    assert detect_marketplace(url="https://www.ajio.com/p/12345") == Marketplace.AJIO


def test_unknown_source_is_other():
    assert detect_marketplace(source_name="Croma", url="https://croma.com/x") == Marketplace.OTHER


def test_no_hints_is_other():
    assert detect_marketplace() == Marketplace.OTHER
