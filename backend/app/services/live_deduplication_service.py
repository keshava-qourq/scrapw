import hashlib

from app.schemas.live_search import LiveProduct
from app.services.deduplication_service import build_match_signature


def deduplicate_live_products(products: list[LiveProduct]) -> list[LiveProduct]:
    """
    Groups live search results that are likely the same real-world product
    across marketplaces, using the same normalized (brand + title) signature
    as the ingested-product pipeline (`build_match_signature`) — deliberately
    conservative, so unrelated products are never merged.

    Every product keeps its own row (nothing is dropped); products sharing a
    signature get the same `duplicate_group` and a confidence score. Gemini
    is intentionally not used here per-product (would burn API quota on every
    search) — this is the seam where an optional secondary AI signal could
    be added later without touching callers.
    """
    groups: dict[str, list[LiveProduct]] = {}
    for product in products:
        signature = build_match_signature(product.title, product.brand)
        if not signature:
            continue
        groups.setdefault(signature, []).append(product)

    for signature, group in groups.items():
        if len(group) < 2:
            continue
        group_id = "grp_" + hashlib.sha1(signature.encode()).hexdigest()[:8]
        for product in group:
            product.duplicate_group = group_id
            # Exact-signature match across a deterministic normalization —
            # high confidence by construction, not a fuzzy/statistical score.
            product.duplicate_confidence = 0.94

    return products
