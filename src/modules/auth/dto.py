import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.modules.users.dto import UserResponse
from src.modules.users.models import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=20)
    role: UserRole
    name: str | None = None
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    identifier: str = Field(..., description='Email or phone number')
    password: str


class AuthResponse(BaseModel):
    access_token: str
    user: UserResponse
