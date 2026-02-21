import logging

from tortoise import Tortoise

from src.core.config import settings

logger = logging.getLogger(__name__)

TORTOISE_ORM = {
    'connections': {
        'default': settings.DATABASE_URL.replace('postgresql://', 'asyncpg://'),
    },
    'apps': {
        'models': {
            'models': [
                'src.modules.users.models',
                'src.modules.offers.models',
                'src.modules.reservations.models',
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
