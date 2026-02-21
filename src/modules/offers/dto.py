from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from .models import OfferStatus


def _validate_location_url(v: str) -> str:
    if not v.startswith(('http://', 'https://')):
        raise ValueError('location_url must start with http:// or https://')
    return v


class CreateOfferRequest(BaseModel):
    description: str = Field(..., min_length=1)
    pickup_from: datetime | None = None
    pickup_to: datetime | None = None
    location_url: str = Field(..., min_length=1)
    photos: list[str] | None = None

    @field_validator('location_url')
    @classmethod
    def validate_location_url(cls, v: str) -> str:
        return _validate_location_url(v)


class UpdateOfferRequest(BaseModel):
    description: str | None = None
    pickup_from: datetime | None = None
    pickup_to: datetime | None = None
    location_url: str | None = None
    photos: list[str] | None = None

    @field_validator('location_url')
    @classmethod
    def validate_location_url(cls, v: str | None) -> str | None:
        if v is not None:
            return _validate_location_url(v)
        return v


class OwnerInfo(BaseModel):
    id: UUID
    name: str | None
    phone_number: str


class OfferResponse(BaseModel):
    id: UUID
    owner_id: UUID
    status: OfferStatus
    description: str
    pickup_from: datetime | None
    pickup_to: datetime | None
    location_url: str
    photos: list[str] | None
    owner: OwnerInfo | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OfferListResponse(BaseModel):
    items: list[OfferResponse]
    total: int
    page: int
    limit: int
