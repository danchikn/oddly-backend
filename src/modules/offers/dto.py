from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .models import OfferStatus


class CreateOfferRequest(BaseModel):
    description: str = Field(..., min_length=1)
    pickup_from: datetime | None = None
    pickup_to: datetime | None = None
    location_url: str = Field(..., min_length=1)
    photos: list[str] | None = None


class UpdateOfferRequest(BaseModel):
    description: str | None = None
    pickup_from: datetime | None = None
    pickup_to: datetime | None = None
    location_url: str | None = None
    photos: list[str] | None = None


class OfferResponse(BaseModel):
    id: UUID
    owner_id: UUID
    status: OfferStatus
    description: str
    pickup_from: datetime | None
    pickup_to: datetime | None
    location_url: str
    photos: list[str] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OfferListResponse(BaseModel):
    items: list[OfferResponse]
    total: int
    page: int
    limit: int
