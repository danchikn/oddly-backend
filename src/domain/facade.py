import secrets
from uuid import UUID

from loguru import logger

from src.clients.smtp import SmtpClient
from src.core.config import settings
from src.worker.schemas import NotificationEvent, VerificationEvent
from src.domain.services.auth_service import AuthService
from src.domain.services.feed_service import FeedService
from src.domain.services.offer_service import OfferService
from src.domain.services.reservation_service import ReservationService
from src.domain.services.review_service import ReviewService
from src.domain.services.user_service import UserService
from src.cache import RedisClient


class Facade:
    def __init__(
        self,
        auth_service: AuthService,
        user_service: UserService,
        offer_service: OfferService,
        feed_service: FeedService,
        reservation_service: ReservationService,
        review_service: ReviewService,
        smtp_client: SmtpClient,
        redis_client: RedisClient,
    ) -> None:
        self._auth = auth_service
        self._user = user_service
        self._offer = offer_service
        self._feed = feed_service
        self._reservation = reservation_service
        self._review = review_service
        self._smtp = smtp_client
        self._redis = redis_client

    # --- Auth ---

    async def register(self, **kwargs):
        return await self._auth.register(**kwargs)

    async def login(self, identifier: str, password: str):
        return await self._auth.login(identifier, password)

    async def verify_email(self, email: str, code: str):
        return await self._auth.verify_email(email, code)

    async def resend_verification(self, email: str):
        return await self._auth.resend_verification(email)

    # --- Users ---

    async def get_user(self, user_id: UUID):
        return await self._user.get_by_id(user_id)

    async def update_user(self, user, data: dict):
        return await self._user.update(user, data)

    async def delete_user(self, user):
        return await self._user.soft_delete(user)

    # --- Offers ---

    async def create_offer(self, owner, data: dict):
        return await self._offer.create(owner, data)

    async def get_offer(self, offer_id: UUID):
        return await self._offer.get_by_id(offer_id)

    async def update_offer(self, offer, user, data: dict):
        return await self._offer.update(offer, user, data)

    async def cancel_offer(self, offer, user):
        return await self._offer.cancel(offer, user)

    async def get_my_offers(self, user, status=None, page: int = 1, limit: int = 20):
        return await self._offer.get_my_offers(user, status=status, page=page, limit=limit)

    # --- Feed ---

    async def get_feed(self, page: int = 1, limit: int = 20, lat: float | None = None, lng: float | None = None):
        return await self._feed.get_feed(page=page, limit=limit, lat=lat, lng=lng)

    # --- Reservations ---

    async def create_reservation(self, farmer, offer_id: UUID):
        return await self._reservation.create(farmer, offer_id)

    async def get_reservation(self, reservation_id: UUID):
        return await self._reservation.get_by_id(reservation_id)

    async def get_reservation_for_user(self, reservation_id: UUID, user):
        return await self._reservation.get_for_user(reservation_id, user)

    async def cancel_reservation(self, reservation, user):
        return await self._reservation.cancel(reservation, user)

    async def complete_reservation(self, reservation, user):
        return await self._reservation.complete(reservation, user)

    async def get_my_reservations(self, user, status=None, page: int = 1, limit: int = 20):
        return await self._reservation.get_my(user, status=status, page=page, limit=limit)

    async def get_incoming_reservations(self, user, status=None, page: int = 1, limit: int = 20):
        return await self._reservation.get_incoming(user, status=status, page=page, limit=limit)

    # --- Reviews ---

    async def create_review(self, author, reservation_id: UUID, rating: int, comment: str | None = None):
        return await self._review.create(author, reservation_id, rating, comment)

    async def get_user_reviews(self, user_id: UUID, page: int = 1, limit: int = 20):
        return await self._review.get_user_reviews(user_id, page=page, limit=limit)

    # --- Consumer handlers ---

    async def handle_verification(self, event: VerificationEvent) -> None:
        code = ''.join(secrets.choice('0123456789') for _ in range(6))

        await self._redis.save_verification_code(event.email, code)

        subject = 'Oddly — Email Verification'
        body = (
            f'Hi {event.name},\n\n'
            f'Your verification code is: {code}\n\n'
            f'This code is valid for {settings.VERIFY_CODE_TTL // 60} minutes.\n\n'
            f'— Oddly Team'
        )
        await self._smtp.send_email(to=event.email, subject=subject, body=body)
        logger.info('Verification email sent: email={}', event.email)

    _NOTIFICATION_TEMPLATES = {
        'reservation.created': {
            'subject': 'Oddly — New Reservation',
            'body': 'Hi {recipient_name},\n\n{farmer_name} has reserved your offer:\n'
                    '"{offer_description}"\n\n— Oddly Team',
        },
        'reservation.cancelled': {
            'subject': 'Oddly — Reservation Cancelled',
            'body': 'Hi {recipient_name},\n\n{farmer_name} has cancelled the reservation for:\n'
                    '"{offer_description}"\n\nYour offer is now open again.\n\n— Oddly Team',
        },
        'reservation.completed': {
            'subject': 'Oddly — Reservation Completed',
            'body': 'Hi {recipient_name},\n\n{owner_name} has confirmed the pickup for:\n'
                    '"{offer_description}"\n\nThank you for using Oddly!\n\n— Oddly Team',
        },
    }

    async def handle_notification(self, event: NotificationEvent) -> None:
        template = self._NOTIFICATION_TEMPLATES.get(event.type)
        if not template:
            logger.warning('Unknown notification type: {}', event.type)
            return

        safe = {k: str(v).replace('{', '').replace('}', '') for k, v in event.model_dump().items()}
        subject = template['subject']
        body = template['body'].format(**safe)

        await self._smtp.send_email(to=event.recipient_email, subject=subject, body=body)
        logger.info('Notification sent: type={}, to={}', event.type, event.recipient_email)
