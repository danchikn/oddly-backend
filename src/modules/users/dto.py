from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.modules.users.models import UserRole


class UserResponse(BaseModel):
    id: UUID
    email: str
    phone_number: str
    role: UserRole
    name: str | None
    status: str

    class Config:
        from_attributes = True


class UserPublicResponse(BaseModel):
    id: UUID
    role: UserRole
    name: str | None

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = Field(None, min_length=5, max_length=20)
