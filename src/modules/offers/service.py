import logging
from uuid import UUID

from src.core.exceptions import NotFoundError
from src.modules.users.models import User

from .dto import CreateOfferRequest, UpdateOfferRequest
from .exceptions import NotOfferOwnerError, OfferNotCancellableError, OfferNotEditableError
from .models import Offer, OfferStatus

logger = logging.getLogger(__name__)

NON_EDITABLE_STATUSES = {OfferStatus.COMPLETED, OfferStatus.CANCELLED}
NON_CANCELLABLE_STATUSES = {OfferStatus.COMPLETED, OfferStatus.CANCELLED}


async def create_offer(owner: User, data: CreateOfferRequest) -> Offer:
    fields = data.model_dump(exclude_none=True)
    offer = await Offer.create(owner=owner, **fields)
    logger.info('Offer created: offer_id=%s, owner_id=%s', offer.id, owner.id)
    return offer


async def get_offer_by_id(offer_id: UUID) -> Offer:
    offer = await Offer.filter(id=offer_id).select_related('owner').first()
    if not offer:
        raise NotFoundError(detail='Offer not found')
    return offer


def check_owner(offer: Offer, user: User) -> None:
    if offer.owner_id != user.id:
        raise NotOfferOwnerError()


async def update_offer(offer: Offer, user: User, data: UpdateOfferRequest) -> Offer:
    check_owner(offer, user)
    if offer.status in NON_EDITABLE_STATUSES:
        raise OfferNotEditableError()
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(offer, key, value)
    await offer.save()
    logger.info('Offer updated: offer_id=%s', offer.id)
    return offer


async def cancel_offer(offer: Offer, user: User) -> Offer:
    check_owner(offer, user)
    if offer.status in NON_CANCELLABLE_STATUSES:
        raise OfferNotCancellableError()
    offer.status = OfferStatus.CANCELLED
    await offer.save()
    logger.info('Offer cancelled: offer_id=%s', offer.id)
    return offer


async def get_my_offers(
    user: User,
    status: OfferStatus | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Offer], int]:
    query = Offer.filter(owner=user)
    if status:
        query = query.filter(status=status)
    total = await query.count()
    items = await query.order_by('-created_at').offset((page - 1) * limit).limit(limit)
    return items, total
