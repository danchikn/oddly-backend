from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    BadRequestError,
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)

STATUS_MAP = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    BadRequestError: status.HTTP_400_BAD_REQUEST,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    ConflictError: status.HTTP_409_CONFLICT,
}


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    for cls, code in STATUS_MAP.items():
        if isinstance(exc, cls):
            status_code = code
            break
    return JSONResponse(status_code=status_code, content={'detail': exc.detail})
