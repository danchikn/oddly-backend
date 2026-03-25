from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from src.domain.models.user import User, UserStatus
from src.domain.repositories.user_repo import UserRepository
from src.domain.services.auth_service import AuthService

security = HTTPBearer()
_user_repo = UserRepository()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    try:
        payload = AuthService.decode_token(credentials.credentials)
    except Exception:
        logger.warning('Invalid or expired token')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')

    user = await _user_repo.get_by_id(payload['sub'])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    if user.status == UserStatus.DELETED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Account deleted')
    if user.status == UserStatus.UNVERIFIED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not verified')
    if user.status == UserStatus.BLOCKED:
        if user.blocked_until is not None and user.blocked_until <= datetime.now(timezone.utc):
            pass
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Account blocked')

    return user
