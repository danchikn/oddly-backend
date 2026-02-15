from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db import close_db, init_db
from src.modules import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title='EcoFeed', version='0.1.0', lifespan=lifespan)

app.include_router(api_router)
