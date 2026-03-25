from fastapi import APIRouter, Depends, Request, status

from src.api.dependencies import get_current_user
from src.api.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, ResendVerifyRequest, VerifyRequest
from src.api.schemas.user import UserResponse
from src.core.rate_limit import limiter
from src.dependencies import get_facade
from src.domain.facade import Facade
from src.domain.models.user import User

router = APIRouter(prefix='/auth', tags=['auth'])


def _user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id, email=user.email, phone_number=user.phone_number,
        role=user.role, name=user.name, location_url=user.location_url,
        status=user.status.value,
    )


@router.post('/register', response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit('3/minute')
async def register(request: Request, body: RegisterRequest, facade: Facade = Depends(get_facade)):
    user, token = await facade.register(
        email=body.email, phone_number=body.phone_number,
        role=body.role, name=body.name, password=body.password,
    )
    return AuthResponse(access_token=token, user=_user_response(user))


@router.post('/login', response_model=AuthResponse)
@limiter.limit('5/minute')
async def login(request: Request, body: LoginRequest, facade: Facade = Depends(get_facade)):
    user, token = await facade.login(body.identifier, body.password)
    return AuthResponse(access_token=token, user=_user_response(user))


@router.post('/verify', response_model=AuthResponse)
async def verify(body: VerifyRequest, facade: Facade = Depends(get_facade)):
    user, token = await facade.verify_email(body.email, body.code)
    return AuthResponse(access_token=token, user=_user_response(user))


@router.post('/resend-verify', status_code=status.HTTP_204_NO_CONTENT)
async def resend_verify(body: ResendVerifyRequest, facade: Facade = Depends(get_facade)):
    await facade.resend_verification(body.email)


@router.get('/me', response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return _user_response(user)
