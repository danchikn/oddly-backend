from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.domain.models.offer import OfferStatus
from src.domain.models.reservation import ReservationStatus


class CreateReservationRequest(BaseModel):
    offer_id: UUID


class ReservationOfferInfo(BaseModel):
    id: UUID
    description: str
    pickup_from: datetime | None
    pickup_to: datetime | None
    location_url: str
    photos: list[str] | None
    status: OfferStatus
    price: float | None = None


class CounterpartyInfo(BaseModel):
    id: UUID
    name: str | None
    phone_number: str


class ReservationResponse(BaseModel):
    id: UUID
    offer_id: UUID
    farmer_id: UUID
    status: ReservationStatus
    payment_status: str = 'UNPAID'
    created_at: datetime
    updated_at: datetime
    offer: ReservationOfferInfo | None = None
    counterparty: CounterpartyInfo | None = None
    has_reviewed: bool = False

    class Config:
        from_attributes = True


class ReservationListResponse(BaseModel):
    items: list[ReservationResponse]
    total: int
    page: int
    limit: int
