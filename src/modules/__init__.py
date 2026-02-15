from fastapi import APIRouter

from .auth.router import router as auth_router
from .feed.router import router as feed_router
from .offers.router import router as offers_router
from .users.router import router as users_router

api_router = APIRouter(prefix='/api')

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(offers_router)
api_router.include_router(feed_router)
