from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.exceptions import UnauthorizedError
from src.modules.users.models import User

from .service import decode_access_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise UnauthorizedError(detail='Invalid or expired token')

    user = await User.filter(id=payload['sub']).first()
    if not user:
        raise UnauthorizedError(detail='User not found')

    return user
