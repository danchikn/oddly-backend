import logging
from datetime import datetime, timezone

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.exceptions import UnauthorizedError
from src.modules.users.models import User, UserStatus

from .service import decode_access_token

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        logger.warning('Invalid or expired token')
        raise UnauthorizedError(detail='Invalid or expired token')

    user = await User.filter(id=payload['sub']).first()
    if not user:
        raise UnauthorizedError(detail='User not found')

    if user.status == UserStatus.DELETED:
        raise UnauthorizedError(detail='Account deleted')

    if user.status == UserStatus.BLOCKED:
        if user.blocked_until is None or user.blocked_until > datetime.now(timezone.utc):
            raise UnauthorizedError(detail='Account blocked')

    return user
