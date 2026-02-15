from tortoise import Tortoise

from src.core.config import settings

TORTOISE_ORM = {
    'connections': {
        'default': settings.DATABASE_URL.replace('postgresql://', 'asyncpg://'),
    },
    'apps': {
        'models': {
            'models': [
                'src.modules.users.models',
                'src.modules.offers.models',
                'aerich.models',
            ],
            'default_connection': 'default',
        },
    },
}


async def init_db() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()
