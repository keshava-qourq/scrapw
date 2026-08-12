from app.schemas.live_search import Marketplace

_DOMAIN_HINTS: dict[str, Marketplace] = {
    "amazon.": Marketplace.AMAZON,
    "flipkart.": Marketplace.FLIPKART,
    "myntra.": Marketplace.MYNTRA,
    "ajio.": Marketplace.AJIO,
}

_NAME_HINTS: dict[str, Marketplace] = {
    "amazon": Marketplace.AMAZON,
    "flipkart": Marketplace.FLIPKART,
    "myntra": Marketplace.MYNTRA,
    "ajio": Marketplace.AJIO,
}


def detect_marketplace(*, source_name: str | None = None, url: str | None = None) -> Marketplace:
    """
    Best-effort marketplace detection from a provider's free-text source name
    and/or product URL. Anything that doesn't clearly match one of the four
    known marketplaces is OTHER — never guessed into a wrong bucket.
    """
    if url:
        url_lower = url.lower()
        for hint, marketplace in _DOMAIN_HINTS.items():
            if hint in url_lower:
                return marketplace

    if source_name:
        name_lower = source_name.lower()
        for hint, marketplace in _NAME_HINTS.items():
            if hint in name_lower:
                return marketplace

    return Marketplace.OTHER
