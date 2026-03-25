import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from prometheus_fastapi_instrumentator import Instrumentator

from src.api.errors import domain_error_handler
from src.api.v1 import router
from src.core.rate_limit import limiter
from src.db import close_db, init_db
from src.domain.exceptions import DomainError
from src.producer import producer_connect, producer_disconnect
from src.cache import RedisClient


def get_configured_app() -> FastAPI:
    redis_client = RedisClient()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(init_db())
                tg.create_task(producer_connect())
                tg.create_task(redis_client.connect())
            yield
        finally:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(close_db())
                tg.create_task(producer_disconnect())
                tg.create_task(redis_client.close())

    app = FastAPI(title='Oddly', version='0.1.0', lifespan=lifespan)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_exception_handler(DomainError, domain_error_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(router)

    Instrumentator().instrument(app).expose(app, endpoint='/metrics')

    return app
