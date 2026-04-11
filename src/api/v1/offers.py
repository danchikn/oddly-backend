from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_current_user
from src.api.schemas.offer import CreateOfferRequest, OfferListResponse, OfferResponse, OwnerInfo, UpdateOfferRequest
from src.dependencies import get_facade
from src.domain.facade import Facade
from src.domain.models.offer import OfferStatus
from src.domain.models.user import User

router = APIRouter(prefix='/offers', tags=['offers'])


def _to_response(offer) -> OfferResponse:
    owner = None
    if hasattr(offer, 'owner') and offer.owner:
        owner = OwnerInfo(id=offer.owner.id, name=offer.owner.name, phone_number=offer.owner.phone_number)
    return OfferResponse(
        id=offer.id, owner_id=offer.owner_id, status=offer.status,
        description=offer.description, pickup_from=offer.pickup_from,
        pickup_to=offer.pickup_to, location_url=offer.location_url,
        photos=offer.photos, owner=owner,
        price=float(offer.price) if offer.price is not None else None,
        created_at=offer.created_at, updated_at=offer.updated_at,
    )


@router.post('', response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create(body: CreateOfferRequest, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    offer = await facade.create_offer(user, body.model_dump(exclude_none=True))
    return _to_response(offer)


@router.get('/my', response_model=OfferListResponse)
async def my_offers(
    status_filter: OfferStatus | None = Query(None, alias='status'),
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user), facade: Facade = Depends(get_facade),
):
    items, total = await facade.get_my_offers(user, status=status_filter, page=page, limit=limit)
    return OfferListResponse(items=[_to_response(o) for o in items], total=total, page=page, limit=limit)


@router.get('/{offer_id}', response_model=OfferResponse)
async def get_one(offer_id: UUID, facade: Facade = Depends(get_facade)):
    return _to_response(await facade.get_offer(offer_id))


@router.patch('/{offer_id}', response_model=OfferResponse)
async def update(offer_id: UUID, body: UpdateOfferRequest, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    offer = await facade.get_offer(offer_id)
    data = body.model_dump(exclude_unset=True)  # use exclude_unset so price=null can clear the field
    offer = await facade.update_offer(offer, user, data)
    return _to_response(offer)


@router.post('/{offer_id}/cancel', response_model=OfferResponse)
async def cancel(offer_id: UUID, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    offer = await facade.get_offer(offer_id)
    offer = await facade.cancel_offer(offer, user)
    return _to_response(offer)
