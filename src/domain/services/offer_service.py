from uuid import UUID

from loguru import logger

from src.domain.geo import parse_coordinates
from src.domain.exceptions import NotFoundError, NotOfferOwnerError, OfferNotCancellableError, OfferNotEditableError
from src.domain.models.offer import OfferStatus
from src.domain.repositories.offer_repo import OfferRepository

NON_EDITABLE = {OfferStatus.COMPLETED, OfferStatus.CANCELLED}
NON_CANCELLABLE = {OfferStatus.COMPLETED, OfferStatus.CANCELLED}


class OfferService:
    def __init__(self, offer_repo: OfferRepository) -> None:
        self._repo = offer_repo

    async def create(self, owner, data: dict):
        coords = parse_coordinates(data.get('location_url', ''))
        if coords:
            data['latitude'], data['longitude'] = coords
        offer = await self._repo.create(owner=owner, **data)
        logger.info('Offer created: offer_id={}, owner_id={}', offer.id, owner.id)
        return offer

    async def get_by_id(self, offer_id: UUID):
        offer = await self._repo.get_by_id(offer_id)
        if not offer:
            raise NotFoundError('Offer not found')
        return offer

    async def update(self, offer, user, data: dict):
        if offer.owner_id != user.id:
            raise NotOfferOwnerError()
        if offer.status in NON_EDITABLE:
            raise OfferNotEditableError()

        for key, value in data.items():
            setattr(offer, key, value)

        if 'location_url' in data:
            coords = parse_coordinates(data['location_url'])
            if coords:
                offer.latitude, offer.longitude = coords
            else:
                offer.latitude, offer.longitude = None, None

        await self._repo.save(offer)
        logger.info('Offer updated: offer_id={}', offer.id)
        return offer

    async def cancel(self, offer, user):
        if offer.owner_id != user.id:
            raise NotOfferOwnerError()
        if offer.status in NON_CANCELLABLE:
            raise OfferNotCancellableError()
        await self._repo.mark_cancelled(offer)
        logger.info('Offer cancelled: offer_id={}', offer.id)
        return offer

    async def get_my_offers(self, user, status=None, page: int = 1, limit: int = 20):
        return await self._repo.get_by_owner(user.id, status=status, page=page, limit=limit)
