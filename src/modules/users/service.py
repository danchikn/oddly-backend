import logging
from uuid import UUID, uuid4

from tortoise.exceptions import IntegrityError

from src.core.exceptions import NotFoundError
from src.modules.auth.exceptions import EmailAlreadyExistsError, PhoneAlreadyExistsError

from .dto import UpdateUserRequest
from .models import User, UserStatus

logger = logging.getLogger(__name__)


async def get_user_by_id(user_id: UUID) -> User:
    user = await User.filter(id=user_id, status=UserStatus.ACTIVE).first()
    if not user:
        raise NotFoundError(detail='User not found')
    return user


async def update_user(user: User, data: UpdateUserRequest) -> User:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(user, key, value)
        
    try:
        await user.save()
    except IntegrityError as e:
        error_msg = str(e).lower()
        if 'email' in error_msg:
            raise EmailAlreadyExistsError() from e
        if 'phone' in error_msg:
            raise PhoneAlreadyExistsError() from e
        raise
    logger.info('User updated profile: user_id=%s', user.id)
    return user


async def soft_delete_user(user: User) -> None:
    suffix = f'_deleted_{uuid4().hex[:8]}'
    user.status = UserStatus.DELETED
    user.email = user.email + suffix
    user.phone_number = user.phone_number + suffix
    await user.save()
    logger.info('User soft-deleted: user_id=%s', user.id)
