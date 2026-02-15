from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.modules.auth.dependencies import get_current_user
from src.modules.users.models import User

from .dto import CreateOfferRequest, OfferListResponse, OfferResponse, UpdateOfferRequest
from .models import OfferStatus
from .service import cancel_offer, create_offer, get_my_offers, get_offer_by_id, update_offer

router = APIRouter(prefix='/offers', tags=['offers'])


def _to_response(offer) -> OfferResponse:
    return OfferResponse(
        id=offer.id,
        owner_id=offer.owner_id,
        status=offer.status,
        description=offer.description,
        pickup_from=offer.pickup_from,
        pickup_to=offer.pickup_to,
        location_url=offer.location_url,
        photos=offer.photos,
        created_at=offer.created_at,
        updated_at=offer.updated_at,
    )


@router.post('', response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create(body: CreateOfferRequest, user: User = Depends(get_current_user)):
    offer = await create_offer(owner=user, data=body)
    return _to_response(offer)


@router.get('/my', response_model=OfferListResponse)
async def my_offers(
    status_filter: OfferStatus | None = Query(None, alias='status'),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    items, total = await get_my_offers(user, status=status_filter, page=page, limit=limit)
    return OfferListResponse(
        items=[_to_response(o) for o in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get('/{offer_id}', response_model=OfferResponse)
async def get_one(offer_id: UUID):
    offer = await get_offer_by_id(offer_id)
    return _to_response(offer)


@router.patch('/{offer_id}', response_model=OfferResponse)
async def update(offer_id: UUID, body: UpdateOfferRequest, user: User = Depends(get_current_user)):
    offer = await get_offer_by_id(offer_id)
    offer = await update_offer(offer, user, data=body)
    return _to_response(offer)


@router.post('/{offer_id}/cancel', response_model=OfferResponse)
async def cancel(offer_id: UUID, user: User = Depends(get_current_user)):
    offer = await get_offer_by_id(offer_id)
    offer = await cancel_offer(offer, user)
    return _to_response(offer)
