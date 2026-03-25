from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from loguru import logger
from tortoise.exceptions import IntegrityError

from src.core.config import settings
from src.domain.exceptions import (
    AccountBlockedError,
    AccountDeletedError,
    AccountNotVerifiedError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidVerificationCodeError,
    PhoneAlreadyExistsError,
)
from src.domain.models.user import UserRole, UserStatus
from src.domain.repositories.user_repo import UserRepository
from src.producer.event_sender import EventSender
from src.cache import RedisClient


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        event_sender: EventSender,
        redis_client: RedisClient,
    ) -> None:
        self._repo = user_repo
        self._events = event_sender
        self._redis = redis_client

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    @staticmethod
    def _create_token(user_id: str, role: str) -> str:
        payload = {
            'sub': user_id,
            'role': role,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

    async def register(
        self,
        email: str,
        phone_number: str,
        role: UserRole,
        name: str | None,
        password: str,
    ) -> tuple:
        if await self._repo.exists_by_email(email):
            raise EmailAlreadyExistsError()
        if await self._repo.exists_by_phone(phone_number):
            raise PhoneAlreadyExistsError()

        try:
            user = await self._repo.create(
                email=email,
                phone_number=phone_number,
                role=role,
                name=name,
                password_hash=self._hash_password(password),
            )
        except IntegrityError as e:
            error_msg = str(e).lower()
            if 'phone' in error_msg:
                raise PhoneAlreadyExistsError() from e
            raise EmailAlreadyExistsError() from e

        token = self._create_token(str(user.id), user.role.value)
        logger.info('User registered: user_id={}, email={}', user.id, user.email)

        await self._events.send_verification({
            'user_id': str(user.id),
            'email': user.email,
            'name': user.name or user.email,
        })

        return user, token

    async def login(self, identifier: str, password: str) -> tuple:
        user = await self._repo.get_by_email(identifier)
        if not user:
            user = await self._repo.get_by_phone(identifier)
        if not user:
            raise InvalidCredentialsError()

        if not self._verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        if user.status == UserStatus.DELETED:
            raise AccountDeletedError()
        if user.status == UserStatus.UNVERIFIED:
            raise AccountNotVerifiedError()
        if user.status == UserStatus.BLOCKED:
            if user.blocked_until is not None and user.blocked_until <= datetime.now(timezone.utc):
                pass
            else:
                raise AccountBlockedError()

        token = self._create_token(str(user.id), user.role.value)
        logger.info('User logged in: user_id={}', user.id)
        return user, token

    async def verify_email(self, email: str, code: str) -> tuple:
        stored_code = await self._redis.get_verification_code(email)
        if not stored_code or stored_code != code:
            raise InvalidVerificationCodeError()

        user = await self._repo.get_unverified_by_email(email)
        if not user:
            raise InvalidVerificationCodeError()

        await self._repo.mark_active(user)
        await self._redis.delete_verification_code(email)

        token = self._create_token(str(user.id), user.role.value)
        logger.info('Email verified: user_id={}', user.id)
        return user, token

    async def resend_verification(self, email: str) -> None:
        user = await self._repo.get_unverified_by_email(email)
        if not user:
            return

        await self._events.send_verification({
            'user_id': str(user.id),
            'email': user.email,
            'name': user.name or user.email,
        })
