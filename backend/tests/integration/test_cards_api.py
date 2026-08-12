import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.deps import get_card_offer_service
from app.main import app
from app.models.card import Card, CardOffer, CardType, OfferType


class FakeCardOfferService:
    def __init__(self):
        self.cards: dict[uuid.UUID, Card] = {}
        self.offers: dict[uuid.UUID, CardOffer] = {}

    async def create_card(self, data):
        card = Card(
            id=uuid.uuid4(),
            bank_name=data.bank_name,
            card_name=data.card_name,
            card_type=data.card_type,
            network=data.network,
        )
        card.created_at = datetime.now(timezone.utc)
        self.cards[card.id] = card
        return card

    async def list_cards(self):
        return list(self.cards.values())

    async def add_offer(self, card_id, data):
        offer = CardOffer(id=uuid.uuid4(), card_id=card_id, **data.model_dump())
        offer.created_at = datetime.now(timezone.utc)
        self.offers[offer.id] = offer
        return offer

    async def list_offers(self, card_id):
        return [o for o in self.offers.values() if o.card_id == card_id]


def test_create_card_and_add_offer():
    fake = FakeCardOfferService()
    app.dependency_overrides[get_card_offer_service] = lambda: fake
    try:
        with TestClient(app) as client:
            card_resp = client.post(
                "/api/v1/cards",
                json={"bank_name": "HDFC", "card_name": "Regalia", "card_type": "credit"},
            )
            card_id = card_resp.json()["id"]

            offer_resp = client.post(
                f"/api/v1/cards/{card_id}/offers",
                json={
                    "title": "10% off on Amazon",
                    "offer_type": "instant_discount",
                    "discount_percentage": 10,
                    "eligible_marketplace": "AMAZON",
                },
            )

            list_resp = client.get(f"/api/v1/cards/{card_id}/offers")
    finally:
        app.dependency_overrides.pop(get_card_offer_service, None)

    assert card_resp.status_code == 201
    assert offer_resp.status_code == 201
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["title"] == "10% off on Amazon"


def test_offer_requires_exactly_one_discount_kind():
    fake = FakeCardOfferService()
    app.dependency_overrides[get_card_offer_service] = lambda: fake
    try:
        with TestClient(app) as client:
            card_resp = client.post(
                "/api/v1/cards",
                json={"bank_name": "HDFC", "card_name": "Regalia"},
            )
            card_id = card_resp.json()["id"]

            both = client.post(
                f"/api/v1/cards/{card_id}/offers",
                json={
                    "title": "bad offer",
                    "offer_type": "instant_discount",
                    "discount_percentage": 10,
                    "discount_flat_amount": 100,
                },
            )
            neither = client.post(
                f"/api/v1/cards/{card_id}/offers",
                json={"title": "bad offer", "offer_type": "instant_discount"},
            )
    finally:
        app.dependency_overrides.pop(get_card_offer_service, None)

    assert both.status_code == 422
    assert neither.status_code == 422
