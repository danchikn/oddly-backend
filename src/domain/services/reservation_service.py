from uuid import UUID

from loguru import logger
from tortoise.transactions import in_transaction

from src.domain.exceptions import (
    NotFarmerError,
    NotFoundError,
    NotReservationParticipantError,
    OfferNotAvailableError,
    ReservationNotCancellableError,
    ReservationNotCompletableError,
)
from src.domain.models.offer import OfferStatus
from src.domain.models.reservation import ReservationStatus
from src.domain.models.user import UserRole
from src.domain.repositories.offer_repo import OfferRepository
from src.domain.repositories.reservation_repo import ReservationRepository
from src.domain.repositories.user_repo import UserRepository
from src.producer.event_sender import EventSender


class ReservationService:
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        offer_repo: OfferRepository,
        user_repo: UserRepository,
        event_sender: EventSender,
    ) -> None:
        self._repo = reservation_repo
        self._offer_repo = offer_repo
        self._user_repo = user_repo
        self._events = event_sender

    async def create(self, farmer, data_offer_id: UUID):
        if farmer.role != UserRole.FARMER:
            raise NotFarmerError()

        async with in_transaction():
            offer = await self._offer_repo.get_by_id_for_update(data_offer_id)
            if not offer:
                raise NotFoundError('Offer not found')
            if offer.status != OfferStatus.OPEN:
                raise OfferNotAvailableError()

            reservation = await self._repo.create(offer=offer, farmer=farmer)
            await self._offer_repo.mark_reserved(offer)

        owner = await self._user_repo.get_by_id(offer.owner_id)
        if owner:
            await self._events.send_notification({
                'type': 'reservation.created',
                'recipient_email': owner.email,
                'recipient_name': owner.name or owner.email,
                'farmer_name': farmer.name or farmer.email,
                'offer_description': offer.description[:100],
            })

        logger.info('Reservation created: id={}, offer={}, farmer={}', reservation.id, data_offer_id, farmer.id)
        return reservation

    async def get_by_id(self, reservation_id: UUID):
        reservation = await self._repo.get_by_id(reservation_id)
        if not reservation:
            raise NotFoundError('Reservation not found')
        return reservation

    async def get_for_user(self, reservation_id: UUID, user):
        reservation = await self._repo.get_by_id(reservation_id)
        if not reservation:
            raise NotFoundError('Reservation not found')

        if reservation.farmer_id == user.id:
            return reservation

        offer = await self._offer_repo.get_by_id(reservation.offer_id)
        if offer and offer.owner_id == user.id:
            return reservation

        raise NotReservationParticipantError()

    async def cancel(self, reservation, user):
        if reservation.farmer_id != user.id:
            raise NotReservationParticipantError()
        if reservation.status != ReservationStatus.ACTIVE:
            raise ReservationNotCancellableError()

        async with in_transaction():
            await self._repo.mark_cancelled(reservation)
            offer = await self._offer_repo.get_by_id_for_update(reservation.offer_id)
            if offer:
                await self._offer_repo.mark_open(offer)

        if offer:
            owner = await self._user_repo.get_by_id(offer.owner_id)
            if owner:
                await self._events.send_notification({
                    'type': 'reservation.cancelled',
                    'recipient_email': owner.email,
                    'recipient_name': owner.name or owner.email,
                    'farmer_name': user.name or user.email,
                    'offer_description': offer.description[:100],
                })

        logger.info('Reservation cancelled: id={}', reservation.id)
        return reservation

    async def complete(self, reservation, user):
        async with in_transaction():
            offer = await self._offer_repo.get_by_id_for_update(reservation.offer_id)
            if not offer or offer.owner_id != user.id:
                raise NotReservationParticipantError()
            if reservation.status != ReservationStatus.ACTIVE:
                raise ReservationNotCompletableError()

            await self._repo.mark_completed(reservation)
            await self._offer_repo.mark_completed(offer)

        farmer = await self._user_repo.get_by_id(reservation.farmer_id)
        if farmer:
            await self._events.send_notification({
                'type': 'reservation.completed',
                'recipient_email': farmer.email,
                'recipient_name': farmer.name or farmer.email,
                'owner_name': user.name or user.email,
                'offer_description': offer.description[:100],
            })

        logger.info('Reservation completed: id={}', reservation.id)
        return reservation

    async def get_my(self, user, status=None, page: int = 1, limit: int = 20):
        return await self._repo.get_by_farmer(user.id, status=status, page=page, limit=limit)

    async def get_incoming(self, user, status=None, page: int = 1, limit: int = 20):
        return await self._repo.get_incoming(user.id, status=status, page=page, limit=limit)
