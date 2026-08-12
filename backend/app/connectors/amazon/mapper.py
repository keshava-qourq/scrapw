from typing import Any

from app.models.product import AvailabilityStatus

_AVAILABILITY_MAP = {
    "Now": AvailabilityStatus.IN_STOCK,
    "OutOfStock": AvailabilityStatus.OUT_OF_STOCK,
    "LimitedAvailability": AvailabilityStatus.LIMITED_STOCK,
}


def map_to_common_schema(parsed: dict[str, Any], marketplace_product_id: str, product_url: str) -> dict[str, Any]:
    price = parsed.get("price")
    mrp = parsed.get("mrp") or price
    discount_percentage = None
    if price is not None and mrp and mrp > 0:
        discount_percentage = round((1 - price / mrp) * 100, 2)

    return {
        "marketplace_code": "amazon",
        "marketplace_product_id": marketplace_product_id,
        "product_url": product_url,
        "name": parsed.get("title") or "Unknown product",
        "brand": parsed.get("brand"),
        "category": None,
        "description": parsed.get("description"),
        "images": [parsed["image_url"]] if parsed.get("image_url") else [],
        "price": price,
        "mrp": mrp,
        "discount_percentage": discount_percentage,
        "currency": parsed.get("currency", "INR"),
        "rating": parsed.get("rating"),
        "review_count": parsed.get("review_count"),
        "availability": _AVAILABILITY_MAP.get(parsed.get("availability"), AvailabilityStatus.UNKNOWN),
        "sizes": [],
        "colors": [],
        "seller_name": "Amazon",
        "seller_rating": None,
        "specifications": {},
        "raw_data": parsed,
    }
