from uuid import UUID, uuid4

from loguru import logger
from tortoise.exceptions import IntegrityError

from src.domain.exceptions import EmailAlreadyExistsError, NotFoundError, PhoneAlreadyExistsError
from src.domain.models.user import User
from src.domain.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def get_by_id(self, user_id: UUID) -> User:
        user = await self._repo.get_active_by_id(user_id)
        if not user:
            raise NotFoundError('User not found')
        return user

    async def update(self, user, data: dict):
        for key, value in data.items():
            setattr(user, key, value)
        try:
            await self._repo.save(user)
        except IntegrityError as e:
            error_msg = str(e).lower()
            if 'email' in error_msg:
                raise EmailAlreadyExistsError() from e
            if 'phone' in error_msg:
                raise PhoneAlreadyExistsError() from e
            raise
        logger.info('User updated: user_id={}', user.id)
        return user

    async def soft_delete(self, user) -> None:
        suffix = f'_deleted_{uuid4().hex[:8]}'
        await self._repo.mark_deleted(user, suffix)
        logger.info('User soft-deleted: user_id={}', user.id)
