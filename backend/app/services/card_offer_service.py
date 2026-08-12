import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.card import Card, CardOffer
from app.schemas.card import CardCreate, CardOfferCreate
from app.schemas.live_search import LiveProduct


def offer_applies_to_product(offer: CardOffer, product: LiveProduct, today: date) -> bool:
    if not offer.is_active:
        return False
    if offer.valid_from is not None and today < offer.valid_from:
        return False
    if offer.valid_until is not None and today > offer.valid_until:
        return False
    if offer.eligible_marketplace is not None and offer.eligible_marketplace != product.marketplace.value:
        return False
    if offer.eligible_category is not None and offer.eligible_category.lower() != (product.category or "").lower():
        return False
    if product.price is None:
        return False
    if offer.min_transaction_amount is not None and product.price < offer.min_transaction_amount:
        return False
    return True


def compute_discount(offer: CardOffer, price: float) -> float:
    if offer.discount_flat_amount is not None:
        discount = offer.discount_flat_amount
    else:
        discount = price * (offer.discount_percentage or 0) / 100

    if offer.max_discount_amount is not None:
        discount = min(discount, offer.max_discount_amount)
    return min(discount, price)


def apply_best_offer(product: LiveProduct, offers: list[CardOffer], today: date | None = None) -> None:
    """Mutates `product` in place, setting `effective_price`/`applied_offer`
    to the single best-matching offer's result, if any offer applies."""
    today = today or date.today()
    applicable = [o for o in offers if offer_applies_to_product(o, product, today)]
    if not applicable or product.price is None:
        return

    best_offer, best_discount = None, 0.0
    for offer in applicable:
        discount = compute_discount(offer, product.price)
        if discount > best_discount:
            best_offer, best_discount = offer, discount

    if best_offer is not None:
        product.effective_price = round(product.price - best_discount, 2)
        product.applied_offer = best_offer.title


class CardOfferService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_card(self, data: CardCreate) -> Card:
        card = Card(**data.model_dump())
        self.session.add(card)
        await self.session.commit()
        await self.session.refresh(card)
        return card

    async def list_cards(self) -> list[Card]:
        result = await self.session.execute(select(Card))
        return list(result.scalars().all())

    async def get_card(self, card_id: uuid.UUID) -> Card:
        card = await self.session.get(Card, card_id)
        if card is None:
            raise NotFoundError(f"Card {card_id} not found")
        return card

    async def add_offer(self, card_id: uuid.UUID, data: CardOfferCreate) -> CardOffer:
        await self.get_card(card_id)  # 404s if the card doesn't exist
        offer = CardOffer(card_id=card_id, **data.model_dump())
        self.session.add(offer)
        await self.session.commit()
        await self.session.refresh(offer)
        return offer

    async def list_offers(self, card_id: uuid.UUID) -> list[CardOffer]:
        result = await self.session.execute(select(CardOffer).where(CardOffer.card_id == card_id))
        return list(result.scalars().all())

    async def delete_offer(self, card_id: uuid.UUID, offer_id: uuid.UUID) -> None:
        offer = await self.session.get(CardOffer, offer_id)
        if offer is None or offer.card_id != card_id:
            raise NotFoundError(f"Offer {offer_id} not found for card {card_id}")
        await self.session.delete(offer)
        await self.session.commit()
