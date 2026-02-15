from fastapi import APIRouter, Query

from src.modules.offers.dto import OfferListResponse, OfferResponse
from src.modules.offers.models import Offer, OfferStatus

router = APIRouter(prefix='/feed', tags=['feed'])


@router.get('', response_model=OfferListResponse)
async def feed(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    query = Offer.filter(status=OfferStatus.OPEN)
    total = await query.count()
    items = await query.order_by('-created_at').offset((page - 1) * limit).limit(limit)
    return OfferListResponse(
        items=[
            OfferResponse(
                id=o.id,
                owner_id=o.owner_id,
                status=o.status,
                description=o.description,
                pickup_from=o.pickup_from,
                pickup_to=o.pickup_to,
                location_url=o.location_url,
                photos=o.photos,
                created_at=o.created_at,
                updated_at=o.updated_at,
            )
            for o in items
        ],
        total=total,
        page=page,
        limit=limit,
    )
