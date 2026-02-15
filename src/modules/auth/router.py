from fastapi import APIRouter, Depends, status

from src.modules.users.dto import UserResponse

from .dependencies import get_current_user
from .dto import AuthResponse, LoginRequest, RegisterRequest
from .service import login_user, register_user

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    user, token = await register_user(
        email=body.email,
        phone_number=body.phone_number,
        role=body.role,
        name=body.name,
        password=body.password,
    )
    return AuthResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            phone_number=user.phone_number,
            role=user.role,
            name=user.name,
            status=user.status.value,
        ),
    )


@router.post('/login', response_model=AuthResponse)
async def login(body: LoginRequest):
    user, token = await login_user(identifier=body.identifier, password=body.password)
    return AuthResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            phone_number=user.phone_number,
            role=user.role,
            name=user.name,
            status=user.status.value,
        ),
    )


@router.get('/me', response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role,
        name=user.name,
        status=user.status.value,
    )
