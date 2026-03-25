from fastapi import APIRouter, Depends, Query

from src.api.schemas.offer import OfferListResponse, OfferResponse, OwnerInfo
from src.dependencies import get_facade
from src.domain.facade import Facade

router = APIRouter(prefix='/feed', tags=['feed'])


def _to_response(o) -> OfferResponse:
    owner = None
    if o.owner:
        owner = OwnerInfo(id=o.owner.id, name=o.owner.name, phone_number=o.owner.phone_number)
    return OfferResponse(
        id=o.id, owner_id=o.owner_id, status=o.status,
        description=o.description, pickup_from=o.pickup_from,
        pickup_to=o.pickup_to, location_url=o.location_url,
        photos=o.photos, owner=owner,
        created_at=o.created_at, updated_at=o.updated_at,
    )


@router.get('', response_model=OfferListResponse)
async def feed(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    lat: float | None = Query(None, ge=-90, le=90),
    lng: float | None = Query(None, ge=-180, le=180),
    facade: Facade = Depends(get_facade),
):
    items, total = await facade.get_feed(page=page, limit=limit, lat=lat, lng=lng)
    return OfferListResponse(items=[_to_response(o) for o in items], total=total, page=page, limit=limit)
