from typing import Any


def parse_flipkart_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract flat fields from a raw Flipkart Affiliate API product feed entry,
    or an equivalently-shaped mock payload.
    https://affiliate.flipkart.com/api-docs/affiliate_api.html
    """
    attrs = payload.get("productBaseInfoV1", payload)
    pricing = attrs.get("flipkartSellingPrice", {})
    mrp = attrs.get("maximumRetailPrice", {})

    return {
        "title": attrs.get("title"),
        "brand": attrs.get("productBrand"),
        "description": attrs.get("description"),
        "category": attrs.get("categoryPath"),
        "image_url": (attrs.get("imageUrls") or {}).get("400x400"),
        "price": pricing.get("amount"),
        "mrp": mrp.get("amount"),
        "currency": pricing.get("currency", "INR"),
        "in_stock": attrs.get("inStock"),
        "rating": attrs.get("productRating"),
        "product_url": attrs.get("productUrl"),
        "product_id": attrs.get("productId"),
    }
