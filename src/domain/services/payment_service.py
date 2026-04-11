import asyncio
from decimal import Decimal
from uuid import UUID

import stripe
from loguru import logger

from src.core.config import settings
from src.domain.exceptions import (
    BadRequestError,
    NotFoundError,
    NotReservationParticipantError,
    OfferHasNoPriceError,
    PaymentNotCompletedError,
    ReservationAlreadyPaidError,
)
from src.domain.models.reservation import ReservationStatus
from src.domain.repositories.reservation_repo import ReservationRepository

MARKUP = Decimal('1.08')


class PaymentService:
    def __init__(self, reservation_repo: ReservationRepository) -> None:
        self._repo = reservation_repo

    def _client(self) -> stripe.StripeClient:
        return stripe.StripeClient(settings.STRIPE_SECRET_KEY)

    async def create_checkout_session(self, user, reservation_id: UUID) -> str:
        reservation = await self._repo.get_by_id(reservation_id)
        if not reservation:
            raise NotFoundError('Reservation not found')
        if reservation.farmer_id != user.id:
            raise NotReservationParticipantError()
        if reservation.status != ReservationStatus.ACTIVE:
            raise BadRequestError('Reservation is not active')
        if reservation.payment_status == 'PAID':
            raise ReservationAlreadyPaidError()

        offer = reservation.offer
        if offer.price is None:
            raise OfferHasNoPriceError()

        amount_tiyn = int(offer.price * MARKUP * 100)

        try:
            session = await asyncio.to_thread(
                lambda: self._client().checkout.sessions.create(params={
                    'payment_method_types': ['card'],
                    'line_items': [{
                        'price_data': {
                            'currency': 'kzt',
                            'product_data': {'name': offer.description[:80]},
                            'unit_amount': amount_tiyn,
                        },
                        'quantity': 1,
                    }],
                    'mode': 'payment',
                    'success_url': f'{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
                    'cancel_url': f'{settings.FRONTEND_URL}/dashboard/reservations',
                    'metadata': {'reservation_id': str(reservation_id)},
                })
            )
        except stripe.StripeError as e:
            raise BadRequestError(f'Failed to create checkout session: {e}')

        reservation.stripe_session_id = session.id
        await self._repo.save(reservation)

        logger.info('Stripe checkout session created: reservation_id={}, session_id={}', reservation_id, session.id)
        return session.url

    async def verify_and_mark_paid(self, session_id: str, user) -> bool:
        try:
            session = await asyncio.to_thread(
                lambda: self._client().checkout.sessions.retrieve(session_id)
            )
        except stripe.StripeError as e:
            raise BadRequestError(f'Stripe error during verification: {e}')

        # Stripe may redirect to success_url before fully processing the payment.
        # Retry once after a short delay to handle this timing gap.
        if session.payment_status != 'paid' or session.status != 'complete':
            await asyncio.sleep(2)
            try:
                session = await asyncio.to_thread(
                    lambda: self._client().checkout.sessions.retrieve(session_id)
                )
            except stripe.StripeError as e:
                raise BadRequestError(f'Stripe error during verification: {e}')

        if session.payment_status != 'paid' or session.status != 'complete':
            raise PaymentNotCompletedError()

        reservation_id = getattr(session.metadata, 'reservation_id', None)
        if not reservation_id:
            raise NotFoundError('Reservation not found in session metadata')

        reservation = await self._repo.get_by_id(UUID(reservation_id))
        if not reservation:
            raise NotFoundError('Reservation not found')
        if reservation.farmer_id != user.id:
            raise NotReservationParticipantError()

        if reservation.payment_status != 'PAID':
            reservation.payment_status = 'PAID'
            await self._repo.save(reservation)
            logger.info('Reservation marked as PAID: reservation_id={}', reservation_id)

        return True
