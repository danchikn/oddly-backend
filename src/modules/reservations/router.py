from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.modules.auth.dependencies import get_current_user
from src.modules.users.models import User

from .dto import CreateReservationRequest, ReservationListResponse, ReservationResponse
from .models import ReservationStatus
from .service import (
    cancel_reservation,
    complete_reservation,
    create_reservation,
    get_incoming_reservations,
    get_my_reservations,
    get_reservation_by_id,
    get_reservation_for_user,
)

router = APIRouter(prefix='/reservations', tags=['reservations'])


def _to_response(reservation) -> ReservationResponse:
    return ReservationResponse(
        id=reservation.id,
        offer_id=reservation.offer_id,
        farmer_id=reservation.farmer_id,
        status=reservation.status,
        created_at=reservation.created_at,
        updated_at=reservation.updated_at,
    )


@router.post('', response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create(body: CreateReservationRequest, user: User = Depends(get_current_user)):
    reservation = await create_reservation(farmer=user, data=body)
    return _to_response(reservation)


@router.get('/my', response_model=ReservationListResponse)
async def my_reservations(
    status_filter: ReservationStatus | None = Query(None, alias='status'),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    items, total = await get_my_reservations(user, status=status_filter, page=page, limit=limit)
    return ReservationListResponse(
        items=[_to_response(r) for r in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get('/incoming', response_model=ReservationListResponse)
async def incoming_reservations(
    status_filter: ReservationStatus | None = Query(None, alias='status'),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    items, total = await get_incoming_reservations(user, status=status_filter, page=page, limit=limit)
    return ReservationListResponse(
        items=[_to_response(r) for r in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get('/{reservation_id}', response_model=ReservationResponse)
async def get_one(reservation_id: UUID, user: User = Depends(get_current_user)):
    reservation = await get_reservation_for_user(reservation_id, user)
    return _to_response(reservation)


@router.post('/{reservation_id}/cancel', response_model=ReservationResponse)
async def cancel(reservation_id: UUID, user: User = Depends(get_current_user)):
    reservation = await get_reservation_by_id(reservation_id)
    reservation = await cancel_reservation(reservation, user)
    return _to_response(reservation)


@router.post('/{reservation_id}/complete', response_model=ReservationResponse)
async def complete(reservation_id: UUID, user: User = Depends(get_current_user)):
    reservation = await get_reservation_by_id(reservation_id)
    reservation = await complete_reservation(reservation, user)
    return _to_response(reservation)
