from loguru import logger

from tortoise import Tortoise

from src.core.config import settings


TORTOISE_ORM = {
    'connections': {
        'default': settings.DATABASE_URL.replace('postgresql://', 'asyncpg://'),
    },
    'apps': {
        'models': {
            'models': [
                'src.domain.models.user',
                'src.domain.models.offer',
                'src.domain.models.reservation',
                'src.domain.models.review',
                'aerich.models',
            ],
            'default_connection': 'default',
        },
    },
}


async def init_db() -> None:
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        logger.info('Database connected')
    except Exception:
        logger.error('Database connection failed', exc_info=True)
        raise


async def close_db() -> None:
    await Tortoise.close_connections()
    logger.info('Database disconnected')
