from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    reservation_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class ReviewOfferInfo(BaseModel):
    id: UUID
    description: str


class ReviewResponse(BaseModel):
    id: UUID
    reservation_id: UUID
    author_id: UUID
    target_id: UUID
    rating: int
    comment: str | None
    author_name: str | None = None
    offer: ReviewOfferInfo | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserRatingResponse(BaseModel):
    average_rating: float | None
    total_reviews: int
    reviews: list[ReviewResponse]
