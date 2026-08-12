from typing import Any

from app.models.product import AvailabilityStatus


def map_to_common_schema(parsed: dict[str, Any], marketplace_product_id: str, product_url: str) -> dict[str, Any]:
    price = parsed.get("price")
    mrp = parsed.get("mrp") or price
    discount_percentage = None
    if price is not None and mrp and mrp > 0:
        discount_percentage = round((1 - price / mrp) * 100, 2)

    availability = AvailabilityStatus.UNKNOWN
    if parsed.get("in_stock") is True:
        availability = AvailabilityStatus.IN_STOCK
    elif parsed.get("in_stock") is False:
        availability = AvailabilityStatus.OUT_OF_STOCK

    return {
        "marketplace_code": "ajio",
        "marketplace_product_id": marketplace_product_id,
        "product_url": product_url,
        "name": parsed.get("title") or "Unknown product",
        "brand": parsed.get("brand"),
        "category": parsed.get("category"),
        "description": parsed.get("description"),
        "images": [parsed["image_url"]] if parsed.get("image_url") else [],
        "price": price,
        "mrp": mrp,
        "discount_percentage": discount_percentage,
        "currency": parsed.get("currency", "INR"),
        "rating": parsed.get("rating"),
        "review_count": parsed.get("review_count"),
        "availability": availability,
        "sizes": parsed.get("sizes", []),
        "colors": parsed.get("colors", []),
        "seller_name": "AJIO",
        "seller_rating": None,
        "specifications": {},
        "raw_data": parsed,
    }
