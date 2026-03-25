from faststream import FastStream
from faststream.rabbit import RabbitBroker
from loguru import logger

from src.core.config import settings
from src.cache import RedisClient
from src.worker.declarations import event_router


async def start_worker() -> None:
    await RedisClient().connect()

    broker = RabbitBroker(url=str(settings.RABBITMQ_URL))
    broker.include_router(event_router)

    app = FastStream(broker, logger=logger)
    await app.run()


__all__ = ('start_worker',)
