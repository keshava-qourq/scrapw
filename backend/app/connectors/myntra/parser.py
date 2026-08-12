from typing import Any


def parse_myntra_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract flat fields from a raw Myntra product payload.

    Myntra has no publicly documented affiliate/partner product-data API at the
    time this connector was written. This parser defines the target shape so a
    real integration can be dropped in without touching downstream code.
    """
    return {
        "title": payload.get("name"),
        "brand": payload.get("brand"),
        "description": payload.get("description"),
        "category": payload.get("category"),
        "image_url": payload.get("imageUrl"),
        "price": payload.get("price"),
        "mrp": payload.get("mrp"),
        "currency": payload.get("currency", "INR"),
        "in_stock": payload.get("inStock"),
        "rating": payload.get("rating"),
        "review_count": payload.get("reviewCount"),
        "sizes": payload.get("sizes", []),
        "colors": payload.get("colors", []),
        "product_id": payload.get("productId"),
        "product_url": payload.get("productUrl"),
    }
