from fastapi import APIRouter

from .auth import router as auth_router
from .feed import router as feed_router
from .offers import router as offers_router
from .reservations import router as reservations_router
from .reviews import router as reviews_router
from .uploads import router as uploads_router
from .users import router as users_router

router = APIRouter(prefix='/api/v1')

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(offers_router)
router.include_router(feed_router)
router.include_router(reservations_router)
router.include_router(reviews_router)
router.include_router(uploads_router)
