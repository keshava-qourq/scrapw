import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_card_offer_service
from app.schemas.card import CardCreate, CardOfferCreate, CardOfferRead, CardRead
from app.services.card_offer_service import CardOfferService

router = APIRouter(prefix="/cards", tags=["cards"])


@router.post("", response_model=CardRead, status_code=201)
async def create_card(
    data: CardCreate,
    service: CardOfferService = Depends(get_card_offer_service),
) -> CardRead:
    return await service.create_card(data)


@router.get("", response_model=list[CardRead])
async def list_cards(service: CardOfferService = Depends(get_card_offer_service)) -> list[CardRead]:
    return await service.list_cards()


@router.post("/{card_id}/offers", response_model=CardOfferRead, status_code=201)
async def add_card_offer(
    card_id: uuid.UUID,
    data: CardOfferCreate,
    service: CardOfferService = Depends(get_card_offer_service),
) -> CardOfferRead:
    return await service.add_offer(card_id, data)


@router.get("/{card_id}/offers", response_model=list[CardOfferRead])
async def list_card_offers(
    card_id: uuid.UUID,
    service: CardOfferService = Depends(get_card_offer_service),
) -> list[CardOfferRead]:
    return await service.list_offers(card_id)


@router.delete("/{card_id}/offers/{offer_id}", status_code=204)
async def delete_card_offer(
    card_id: uuid.UUID,
    offer_id: uuid.UUID,
    service: CardOfferService = Depends(get_card_offer_service),
) -> None:
    await service.delete_offer(card_id, offer_id)
