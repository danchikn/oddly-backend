from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_current_user
from src.api.schemas.reservation import CreateReservationRequest, ReservationListResponse, ReservationResponse
from src.dependencies import get_facade
from src.domain.facade import Facade
from src.domain.models.reservation import ReservationStatus
from src.domain.models.user import User

router = APIRouter(prefix='/reservations', tags=['reservations'])


def _to_response(r) -> ReservationResponse:
    return ReservationResponse(
        id=r.id, offer_id=r.offer_id, farmer_id=r.farmer_id,
        status=r.status, created_at=r.created_at, updated_at=r.updated_at,
    )


@router.post('', response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create(body: CreateReservationRequest, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    reservation = await facade.create_reservation(user, body.offer_id)
    return _to_response(reservation)


@router.get('/my', response_model=ReservationListResponse)
async def my_reservations(
    status_filter: ReservationStatus | None = Query(None, alias='status'),
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user), facade: Facade = Depends(get_facade),
):
    items, total = await facade.get_my_reservations(user, status=status_filter, page=page, limit=limit)
    return ReservationListResponse(items=[_to_response(r) for r in items], total=total, page=page, limit=limit)


@router.get('/incoming', response_model=ReservationListResponse)
async def incoming(
    status_filter: ReservationStatus | None = Query(None, alias='status'),
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user), facade: Facade = Depends(get_facade),
):
    items, total = await facade.get_incoming_reservations(user, status=status_filter, page=page, limit=limit)
    return ReservationListResponse(items=[_to_response(r) for r in items], total=total, page=page, limit=limit)


@router.get('/{reservation_id}', response_model=ReservationResponse)
async def get_one(reservation_id: UUID, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    return _to_response(await facade.get_reservation_for_user(reservation_id, user))


@router.post('/{reservation_id}/cancel', response_model=ReservationResponse)
async def cancel(reservation_id: UUID, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    reservation = await facade.get_reservation(reservation_id)
    return _to_response(await facade.cancel_reservation(reservation, user))


@router.post('/{reservation_id}/complete', response_model=ReservationResponse)
async def complete(reservation_id: UUID, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    reservation = await facade.get_reservation(reservation_id)
    return _to_response(await facade.complete_reservation(reservation, user))
