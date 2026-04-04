from src.domain.repositories.offer_repo import OfferRepository


class FeedService:
    def __init__(self, offer_repo: OfferRepository) -> None:
        self._repo = offer_repo

    async def get_feed(self, page: int = 1, limit: int = 20, lat: float | None = None, lng: float | None = None, q: str | None = None):
        return await self._repo.get_open_feed(page=page, limit=limit, lat=lat, lng=lng, q=q)
