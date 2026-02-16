from uuid import UUID

from tortoise.transactions import in_transaction

from src.core.exceptions import NotFoundError
from src.modules.offers.models import Offer, OfferStatus
from src.modules.users.models import User, UserRole

from .dto import CreateReservationRequest
from .exceptions import (
    NotFarmerError,
    NotReservationParticipantError,
    OfferNotAvailableError,
    ReservationNotCancellableError,
    ReservationNotCompletableError,
)
from .models import Reservation, ReservationStatus


async def create_reservation(farmer: User, data: CreateReservationRequest) -> Reservation:
    if farmer.role != UserRole.FARMER:
        raise NotFarmerError()

    async with in_transaction():
        offer = await Offer.filter(id=data.offer_id).select_for_update().first()
        if not offer:
            raise NotFoundError(detail='Offer not found')
        if offer.status != OfferStatus.OPEN:
            raise OfferNotAvailableError()

        reservation = await Reservation.create(offer=offer, farmer=farmer)
        offer.status = OfferStatus.RESERVED
        await offer.save()
    return reservation


async def get_reservation_by_id(reservation_id: UUID) -> Reservation:
    reservation = await Reservation.filter(id=reservation_id).first()
    if not reservation:
        raise NotFoundError(detail='Reservation not found')
    return reservation


async def cancel_reservation(reservation: Reservation, user: User) -> Reservation:
    if reservation.farmer_id != user.id:
        raise NotReservationParticipantError()
    if reservation.status != ReservationStatus.ACTIVE:
        raise ReservationNotCancellableError()

    async with in_transaction():
        reservation.status = ReservationStatus.CANCELLED
        await reservation.save()

        offer = await Offer.filter(id=reservation.offer_id).select_for_update().first()
        if offer:
            offer.status = OfferStatus.OPEN
            await offer.save()

    return reservation


async def complete_reservation(reservation: Reservation, user: User) -> Reservation:
    async with in_transaction():
        offer = await Offer.filter(id=reservation.offer_id).select_for_update().first()
        if not offer or offer.owner_id != user.id:
            raise NotReservationParticipantError()
        if reservation.status != ReservationStatus.ACTIVE:
            raise ReservationNotCompletableError()

        reservation.status = ReservationStatus.COMPLETED
        await reservation.save()

        offer.status = OfferStatus.COMPLETED
        await offer.save()

    return reservation


async def get_my_reservations(
    user: User,
    status: ReservationStatus | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Reservation], int]:
    query = Reservation.filter(farmer=user)
    if status:
        query = query.filter(status=status)
    total = await query.count()
    items = await query.order_by('-created_at').offset((page - 1) * limit).limit(limit)
    return items, total
