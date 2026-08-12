from datetime import datetime, timezone
from typing import Any

from app.schemas.live_search import Availability, LiveProduct
from app.services.marketplace_detector import detect_marketplace


def _parse_price(value: Any) -> float | None:
    """SerpApi's `extracted_price` is already numeric when present; the
    plain `price` field is a display string (e.g. "₹79,999.00") we won't
    trust for filtering/sorting, only for display fallback."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_serpapi_shopping_result(item: dict[str, Any], *, source: str = "serpapi") -> LiveProduct | None:
    """
    Maps one SerpApi `google_shopping` `shopping_results` entry onto the
    common `LiveProduct` shape. Returns None if the item is missing the
    fields a product can't be shown without (title, link) — never fabricates
    them.
    """
    title = item.get("title")
    product_url = item.get("product_link") or item.get("link")
    if not title or not product_url:
        return None

    price = _parse_price(item.get("extracted_price"))
    original_price = _parse_price(item.get("extracted_original_price"))
    discount_percentage = None
    if price is not None and original_price is not None and original_price > 0:
        discount_percentage = round((1 - price / original_price) * 100, 2)

    source_name = item.get("source")
    marketplace = detect_marketplace(source_name=source_name, url=product_url)

    review_count_raw = item.get("reviews")
    review_count = int(review_count_raw) if isinstance(review_count_raw, (int, float)) else None

    product_id = item.get("product_id") or product_url

    return LiveProduct(
        id=f"serpapi_{product_id}",
        title=title,
        brand=item.get("brand"),
        marketplace=marketplace,
        seller=source_name,
        price=price,
        original_price=original_price,
        discount_percentage=discount_percentage,
        rating=item.get("rating"),
        review_count=review_count,
        image_url=item.get("thumbnail"),
        product_url=product_url,
        availability=Availability.UNKNOWN,
        category=None,
        source=source,
        scraped_at=datetime.now(timezone.utc),
    )
