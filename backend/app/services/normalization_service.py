from typing import Any

from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import ValidationError
from app.schemas.product import ProductCreate


class NormalizationService:
    """
    Stage of the ingestion pipeline that takes a connector's
    `normalize_product()` output (already mapped onto common field names) and
    validates/cleans it into a `ProductCreate`.

    Kept separate from connectors so validation rules are identical across all
    marketplaces, and separate from persistence so it stays unit-testable.
    """

    @staticmethod
    def normalize(raw: dict[str, Any]) -> ProductCreate:
        cleaned = dict(raw)

        if cleaned.get("name"):
            cleaned["name"] = " ".join(str(cleaned["name"]).split())
        if cleaned.get("brand"):
            cleaned["brand"] = str(cleaned["brand"]).strip()

        price = cleaned.get("price")
        mrp = cleaned.get("mrp")
        if price is not None and price < 0:
            raise ValidationError("price cannot be negative")
        if mrp is not None and mrp < 0:
            raise ValidationError("mrp cannot be negative")

        if cleaned.get("discount_percentage") is None and price is not None and mrp:
            cleaned["discount_percentage"] = NormalizationService.calculate_discount(price, mrp)

        cleaned["images"] = [img for img in (cleaned.get("images") or []) if img]
        cleaned["sizes"] = [s for s in (cleaned.get("sizes") or []) if s]
        cleaned["colors"] = [c for c in (cleaned.get("colors") or []) if c]

        try:
            return ProductCreate(**cleaned)
        except PydanticValidationError as exc:
            raise ValidationError(f"Product failed validation: {exc}") from exc

    @staticmethod
    def calculate_discount(price: float, mrp: float) -> float | None:
        if not mrp or mrp <= 0 or price is None:
            return None
        return round(max(0.0, (1 - price / mrp) * 100), 2)
