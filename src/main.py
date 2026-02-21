import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.core.logging import setup_logging
from src.core.rate_limit import limiter
from src.db import close_db, init_db
from src.modules import api_router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Application startup')
    await init_db()
    yield
    await close_db()
    logger.info('Application shutdown')


app = FastAPI(title='EcoFeed', version='0.1.0', lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # TODO: replace with specific domain in production
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router)
