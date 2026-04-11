from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_current_user
from src.dependencies import get_facade
from src.domain.facade import Facade
from src.domain.models.user import User

router = APIRouter(tags=['payments'])


@router.post('/reservations/{reservation_id}/checkout')
async def create_checkout(
    reservation_id: UUID,
    user: User = Depends(get_current_user),
    facade: Facade = Depends(get_facade),
):
    checkout_url = await facade.create_checkout_session(user, reservation_id)
    return {'checkout_url': checkout_url}


@router.get('/payments/verify')
async def verify_payment(
    session_id: str = Query(...),
    user: User = Depends(get_current_user),
    facade: Facade = Depends(get_facade),
):
    await facade.verify_payment(session_id, user)
    return {'paid': True}
