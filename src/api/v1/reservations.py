from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_current_user
from src.api.schemas.reservation import (
    CounterpartyInfo,
    CreateReservationRequest,
    ReservationListResponse,
    ReservationOfferInfo,
    ReservationResponse,
)
from src.dependencies import get_facade
from src.domain.facade import Facade
from src.domain.models.reservation import ReservationStatus
from src.domain.models.user import User

router = APIRouter(prefix='/reservations', tags=['reservations'])


def _offer_info(offer) -> ReservationOfferInfo | None:
    if not offer:
        return None
    return ReservationOfferInfo(
        id=offer.id,
        description=offer.description,
        pickup_from=offer.pickup_from,
        pickup_to=offer.pickup_to,
        location_url=offer.location_url,
        photos=offer.photos,
        status=offer.status,
    )


def _counterparty_info(user_obj) -> CounterpartyInfo | None:
    if not user_obj:
        return None
    return CounterpartyInfo(
        id=user_obj.id,
        name=user_obj.name,
        phone_number=user_obj.phone_number,
    )


def _to_response(r, *, current_user: User | None = None, reviewed_ids: set | None = None) -> ReservationResponse:
    offer = getattr(r, 'offer', None)
    farmer = getattr(r, 'farmer', None)
    owner = getattr(offer, 'owner', None) if offer else None

    counterparty = None
    if current_user:
        if current_user.id == r.farmer_id:
            counterparty = _counterparty_info(owner)
        else:
            counterparty = _counterparty_info(farmer)

    has_reviewed = False
    if reviewed_ids is not None:
        has_reviewed = r.id in reviewed_ids

    return ReservationResponse(
        id=r.id,
        offer_id=r.offer_id,
        farmer_id=r.farmer_id,
        status=r.status,
        created_at=r.created_at,
        updated_at=r.updated_at,
        offer=_offer_info(offer),
        counterparty=counterparty,
        has_reviewed=has_reviewed,
    )


async def _build_list_response(
    items, total: int, page: int, limit: int,
    user: User, facade: Facade,
) -> ReservationListResponse:
    reservation_ids = [r.id for r in items]
    reviewed_ids = await facade.get_reviewed_reservation_ids(reservation_ids, user.id) if reservation_ids else set()
    return ReservationListResponse(
        items=[_to_response(r, current_user=user, reviewed_ids=reviewed_ids) for r in items],
        total=total, page=page, limit=limit,
    )


@router.post('', response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create(body: CreateReservationRequest, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    reservation = await facade.create_reservation(user, body.offer_id)
    reservation = await facade.get_reservation(reservation.id)
    return _to_response(reservation, current_user=user)


@router.get('/my', response_model=ReservationListResponse)
async def my_reservations(
    status_filter: ReservationStatus | None = Query(None, alias='status'),
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user), facade: Facade = Depends(get_facade),
):
    items, total = await facade.get_my_reservations(user, status=status_filter, page=page, limit=limit)
    return await _build_list_response(items, total, page, limit, user, facade)


@router.get('/incoming', response_model=ReservationListResponse)
async def incoming(
    status_filter: ReservationStatus | None = Query(None, alias='status'),
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user), facade: Facade = Depends(get_facade),
):
    items, total = await facade.get_incoming_reservations(user, status=status_filter, page=page, limit=limit)
    return await _build_list_response(items, total, page, limit, user, facade)


@router.get('/{reservation_id}', response_model=ReservationResponse)
async def get_one(reservation_id: UUID, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    r = await facade.get_reservation_for_user(reservation_id, user)
    reviewed_ids = await facade.get_reviewed_reservation_ids([r.id], user.id)
    return _to_response(r, current_user=user, reviewed_ids=reviewed_ids)


@router.post('/{reservation_id}/cancel', response_model=ReservationResponse)
async def cancel(reservation_id: UUID, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    reservation = await facade.get_reservation(reservation_id)
    await facade.cancel_reservation(reservation, user)
    reservation = await facade.get_reservation(reservation_id)
    return _to_response(reservation, current_user=user)


@router.post('/{reservation_id}/complete', response_model=ReservationResponse)
async def complete(reservation_id: UUID, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    reservation = await facade.get_reservation(reservation_id)
    await facade.complete_reservation(reservation, user)
    reservation = await facade.get_reservation(reservation_id)
    return _to_response(reservation, current_user=user)
