import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import CanonicalProduct, Product

# Words that don't help distinguish one product from another (marketing/gender
# filler, common across marketplace listings of the *same* underlying product).
_STOPWORDS = {
    "men", "mens", "men's", "women", "womens", "women's", "unisex",
    "the", "a", "an", "for", "with", "and",
}
_APOSTROPHE = re.compile(r"['’]")
_NON_ALNUM = re.compile(r"[^a-z0-9 ]")


def build_match_signature(name: str, brand: str | None) -> str:
    """
    Basic, deterministic normalization used to group listings of the same
    product across marketplaces: lowercase, strip punctuation, drop filler
    words, sort remaining tokens.

    This is intentionally simple. It is designed to be swapped out later for
    an embedding/AI-based similarity match without changing any caller — see
    DeduplicationService.find_canonical_match.
    """
    text = f"{brand or ''} {name}".lower()
    text = _APOSTROPHE.sub("", text)
    text = _NON_ALNUM.sub(" ", text)
    tokens = [t for t in text.split() if t and t not in _STOPWORDS]
    return " ".join(sorted(tokens))


class DeduplicationService:
    """
    Groups `Product` rows from different marketplaces that represent the same
    real-world product under a shared `CanonicalProduct`.

    Current strategy: exact match on a normalized (brand + name) signature.
    Extensible: `find_canonical_match` is the single seam to replace with a
    fuzzy/embedding-based matcher later without touching ingestion callers.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_canonical_match(self, name: str, brand: str | None) -> CanonicalProduct | None:
        signature = build_match_signature(name, brand)
        if not signature:
            return None

        result = await self.session.execute(select(CanonicalProduct).where(CanonicalProduct.brand == brand))
        for candidate in result.scalars().all():
            if build_match_signature(candidate.name, candidate.brand) == signature:
                return candidate
        return None

    async def assign_canonical_product(self, product: Product) -> CanonicalProduct:
        match = await self.find_canonical_match(product.name, product.brand)
        if match is None:
            match = CanonicalProduct(name=product.name, brand=product.brand, category=product.category)
            self.session.add(match)
            await self.session.flush()
        else:
            match.updated_at = datetime.now(timezone.utc)

        product.canonical_product_id = match.id
        await self.session.flush()
        return match
