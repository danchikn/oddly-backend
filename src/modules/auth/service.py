import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from tortoise.exceptions import IntegrityError

from src.core.config import settings
from src.modules.users.models import User, UserRole, UserStatus

from .exceptions import (
    AccountBlockedError,
    AccountDeletedError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    PhoneAlreadyExistsError,
)

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: str, role: str) -> str:
    payload = {
        'sub': user_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


async def register_user(
    email: str,
    phone_number: str,
    role: UserRole,
    name: str | None,
    password: str,
) -> tuple[User, str]:
    if await User.filter(email=email).exists():
        raise EmailAlreadyExistsError()
    if await User.filter(phone_number=phone_number).exists():
        raise PhoneAlreadyExistsError()

    try:
        user = await User.create(
            email=email,
            phone_number=phone_number,
            role=role,
            name=name,
            password_hash=hash_password(password),
        )
    except IntegrityError as e:
        logger.warning('IntegrityError during registration: %s', e)
        raise EmailAlreadyExistsError() from e

    token = create_access_token(str(user.id), user.role.value)
    logger.info('User registered: user_id=%s, email=%s, role=%s', user.id, user.email, user.role.value)
    return user, token


async def login_user(identifier: str, password: str) -> tuple[User, str]:
    user = await User.filter(email=identifier).first()
    if not user:
        user = await User.filter(phone_number=identifier).first()
    if not user:
        logger.warning('Failed login attempt: identifier=%s, reason=not_found', identifier)
        raise InvalidCredentialsError()

    if not verify_password(password, user.password_hash):
        logger.warning('Failed login attempt: identifier=%s, reason=wrong_password', identifier)
        raise InvalidCredentialsError()

    if user.status == UserStatus.DELETED:
        raise AccountDeletedError()

    if user.status == UserStatus.BLOCKED:
        if user.blocked_until and user.blocked_until > datetime.now(timezone.utc):
            logger.warning('Blocked account login attempt: user_id=%s', user.id)
            raise AccountBlockedError()

    token = create_access_token(str(user.id), user.role.value)
    logger.info('User logged in: user_id=%s', user.id)
    return user, token
