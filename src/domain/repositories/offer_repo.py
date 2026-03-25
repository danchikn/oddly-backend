from uuid import UUID

from src.domain.models.offer import Offer, OfferStatus


class OfferRepository:
    async def get_by_id(self, offer_id: UUID) -> Offer | None:
        return await Offer.filter(id=offer_id).select_related('owner').first()

    async def get_by_id_for_update(self, offer_id: UUID) -> Offer | None:
        return await Offer.filter(id=offer_id).select_for_update().first()

    async def create(self, **kwargs) -> Offer:
        return await Offer.create(**kwargs)

    async def save(self, offer: Offer) -> None:
        await offer.save()

    async def mark_reserved(self, offer: Offer) -> None:
        offer.status = OfferStatus.RESERVED
        await offer.save()

    async def mark_open(self, offer: Offer) -> None:
        offer.status = OfferStatus.OPEN
        await offer.save()

    async def mark_completed(self, offer: Offer) -> None:
        offer.status = OfferStatus.COMPLETED
        await offer.save()

    async def mark_cancelled(self, offer: Offer) -> None:
        offer.status = OfferStatus.CANCELLED
        await offer.save()

    async def get_by_owner(
        self,
        owner_id: 'UUID',
        status: OfferStatus | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Offer], int]:
        query = Offer.filter(owner_id=owner_id).select_related('owner')
        if status:
            query = query.filter(status=status)
        total = await query.count()
        items = await query.order_by('-created_at').offset((page - 1) * limit).limit(limit)
        return items, total

    async def get_open_feed(
        self,
        page: int = 1,
        limit: int = 20,
        lat: float | None = None,
        lng: float | None = None,
    ) -> tuple[list[Offer], int]:
        from tortoise.expressions import RawSQL

        query = Offer.filter(status=OfferStatus.OPEN).select_related('owner')
        total = await query.count()

        if lat is not None and lng is not None:
            haversine = (
                f'6371 * acos('
                f'cos(radians({lat})) * cos(radians(latitude))'
                f' * cos(radians(longitude) - radians({lng}))'
                f' + sin(radians({lat})) * sin(radians(latitude)))'
            )
            items = await (
                query
                .filter(latitude__isnull=False)
                .annotate(distance=RawSQL(haversine))
                .order_by('distance')
                .offset((page - 1) * limit)
                .limit(limit)
            )
            remaining = limit - len(items)
            if remaining > 0:
                no_geo = await (
                    Offer.filter(status=OfferStatus.OPEN, latitude__isnull=True)
                    .select_related('owner')
                    .order_by('-created_at')
                    .limit(remaining)
                )
                items = list(items) + list(no_geo)
        else:
            items = await query.order_by('-created_at').offset((page - 1) * limit).limit(limit)

        return items, total
