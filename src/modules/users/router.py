from uuid import UUID

from fastapi import APIRouter, Depends

from src.modules.auth.dependencies import get_current_user
from src.modules.users.models import User

from .dto import UpdateUserRequest, UserPublicResponse, UserResponse
from .service import get_user_by_id, soft_delete_user, update_user

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/{user_id}', response_model=UserPublicResponse)
async def get_user(user_id: UUID):
    user = await get_user_by_id(user_id)
    return UserPublicResponse(
        id=user.id,
        role=user.role,
        name=user.name,
    )


@router.patch('/me', response_model=UserResponse)
async def update_me(body: UpdateUserRequest, user: User = Depends(get_current_user)):
    user = await update_user(user, data=body)
    return UserResponse(
        id=user.id,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role,
        name=user.name,
        location_url=user.location_url,
        status=user.status.value,
    )


@router.post('/me/delete', status_code=204)
async def delete_me(user: User = Depends(get_current_user)):
    await soft_delete_user(user)
