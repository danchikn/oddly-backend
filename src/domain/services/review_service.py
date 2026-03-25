from uuid import UUID

from loguru import logger

from src.domain.exceptions import (
    AlreadyReviewedError,
    CannotReviewSelfError,
    NotFoundError,
    NotReservationParticipantError,
    ReservationNotCompletedError,
)
from src.domain.models.reservation import ReservationStatus
from src.domain.repositories.offer_repo import OfferRepository
from src.domain.repositories.reservation_repo import ReservationRepository
from src.domain.repositories.review_repo import ReviewRepository


class ReviewService:
    def __init__(
        self,
        review_repo: ReviewRepository,
        reservation_repo: ReservationRepository,
        offer_repo: OfferRepository,
    ) -> None:
        self._repo = review_repo
        self._reservation_repo = reservation_repo
        self._offer_repo = offer_repo

    async def create(self, author, reservation_id: UUID, rating: int, comment: str | None):
        reservation = await self._reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise NotFoundError('Reservation not found')
        if reservation.status != ReservationStatus.COMPLETED:
            raise ReservationNotCompletedError()

        offer = await self._offer_repo.get_by_id(reservation.offer_id)
        if not offer:
            raise NotFoundError('Offer not found')

        if author.id == reservation.farmer_id:
            target_id = offer.owner_id
        elif author.id == offer.owner_id:
            target_id = reservation.farmer_id
        else:
            raise NotReservationParticipantError()

        if target_id == author.id:
            raise CannotReviewSelfError()
        if await self._repo.exists(reservation_id, author.id):
            raise AlreadyReviewedError()

        review = await self._repo.create(
            reservation_id=reservation_id,
            author_id=author.id,
            target_id=target_id,
            rating=rating,
            comment=comment,
        )
        logger.info('Review created: id={}, author={}, target={}', review.id, author.id, target_id)
        return review

    async def get_user_reviews(self, user_id: UUID, page: int = 1, limit: int = 20):
        return await self._repo.get_by_target(user_id, page=page, limit=limit)
