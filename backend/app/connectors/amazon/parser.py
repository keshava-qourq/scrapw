from typing import Any


def parse_amazon_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract flat fields from a raw Amazon Product Advertising API (PA-API 5.0)
    `Item` payload, or an equivalently-shaped mock payload.

    Expected shape (subset of PA-API 5.0's GetItems/SearchItems response):
    https://webservices.amazon.com/paapi5/documentation/get-items.html
    """
    item_info = payload.get("ItemInfo", {})
    offers = payload.get("Offers", {}).get("Listings", [{}])
    listing = offers[0] if offers else {}
    price_info = listing.get("Price", {})
    saving_basis = listing.get("SavingBasis", {})
    images = payload.get("Images", {}).get("Primary", {})

    title = item_info.get("Title", {}).get("DisplayValue")
    brand = item_info.get("ByLineInfo", {}).get("Brand", {}).get("DisplayValue")
    features = item_info.get("Features", {}).get("DisplayValues", [])

    return {
        "title": title,
        "brand": brand,
        "description": " ".join(features) if features else None,
        "image_url": images.get("Large", {}).get("URL"),
        "price": price_info.get("Amount"),
        "mrp": saving_basis.get("Amount") or price_info.get("Amount"),
        "currency": price_info.get("Currency", "INR"),
        "availability": listing.get("Availability", {}).get("Type"),
        "rating": payload.get("CustomerReviews", {}).get("StarRating"),
        "review_count": payload.get("CustomerReviews", {}).get("Count"),
        "detail_page_url": payload.get("DetailPageURL"),
        "asin": payload.get("ASIN"),
    }
