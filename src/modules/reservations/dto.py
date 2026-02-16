from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .models import ReservationStatus


class CreateReservationRequest(BaseModel):
    offer_id: UUID


class ReservationResponse(BaseModel):
    id: UUID
    offer_id: UUID
    farmer_id: UUID
    status: ReservationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReservationListResponse(BaseModel):
    items: list[ReservationResponse]
    total: int
    page: int
    limit: int
