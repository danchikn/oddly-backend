from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_user
from src.api.schemas.user import UpdateUserRequest, UserPublicResponse, UserResponse
from src.dependencies import get_facade
from src.domain.facade import Facade
from src.domain.models.user import User

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/{user_id}', response_model=UserPublicResponse)
async def get_user(user_id: UUID, facade: Facade = Depends(get_facade)):
    user = await facade.get_user(user_id)
    return UserPublicResponse(id=user.id, role=user.role, name=user.name)


@router.patch('/me', response_model=UserResponse)
async def update_me(body: UpdateUserRequest, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    user = await facade.update_user(user, body.model_dump(exclude_none=True))
    return UserResponse(
        id=user.id, email=user.email, phone_number=user.phone_number,
        role=user.role, name=user.name, location_url=user.location_url,
        status=user.status.value,
    )


@router.post('/me/delete', status_code=204)
async def delete_me(user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    await facade.delete_user(user)
