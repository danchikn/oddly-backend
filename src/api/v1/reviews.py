from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_current_user
from src.api.schemas.review import CreateReviewRequest, ReviewResponse, UserRatingResponse
from src.dependencies import get_facade
from src.domain.facade import Facade
from src.domain.models.user import User

router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.post('', response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(body: CreateReviewRequest, user: User = Depends(get_current_user), facade: Facade = Depends(get_facade)):
    review = await facade.create_review(user, body.reservation_id, body.rating, body.comment)
    return ReviewResponse(
        id=review.id, reservation_id=review.reservation_id,
        author_id=review.author_id, target_id=review.target_id,
        rating=review.rating, comment=review.comment,
        created_at=review.created_at,
    )


@router.get('/user/{user_id}', response_model=UserRatingResponse)
async def get_user_reviews(user_id: UUID, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), facade: Facade = Depends(get_facade)):
    reviews, total, avg_rating = await facade.get_user_reviews(user_id, page=page, limit=limit)
    return UserRatingResponse(
        average_rating=round(avg_rating, 2) if avg_rating is not None else None,
        total_reviews=total,
        reviews=[
            ReviewResponse(
                id=r.id, reservation_id=r.reservation_id,
                author_id=r.author_id, target_id=r.target_id,
                rating=r.rating, comment=r.comment,
                author_name=r.author.name if r.author else None,
                created_at=r.created_at,
            ) for r in reviews
        ],
    )
