from uuid import UUID

from src.domain.models.review import Review


class ReviewRepository:
    async def exists(self, reservation_id: UUID, author_id: UUID) -> bool:
        return await Review.filter(reservation_id=reservation_id, author_id=author_id).exists()

    async def create(self, **kwargs) -> Review:
        return await Review.create(**kwargs)

    async def get_by_target(
        self,
        target_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Review], int, float | None]:
        from tortoise.functions import Avg

        query = Review.filter(target_id=target_id)
        total = await query.count()
        reviews = await (
            query
            .select_related('author')
            .order_by('-created_at')
            .offset((page - 1) * limit)
            .limit(limit)
        )
        stats = await Review.filter(target_id=target_id).annotate(
            avg_rating=Avg('rating'),
        ).values('avg_rating')
        avg = stats[0]['avg_rating'] if stats else None
        return reviews, total, avg
