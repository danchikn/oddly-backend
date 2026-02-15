from pydantic import BaseModel, EmailStr, Field

from src.modules.users.dto import UserResponse
from src.modules.users.models import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=20)
    role: UserRole
    name: str | None = None
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    identifier: str = Field(..., description='Email or phone number')
    password: str


class AuthResponse(BaseModel):
    access_token: str
    user: UserResponse
