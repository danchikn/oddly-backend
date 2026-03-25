from loguru import logger

import redis.asyncio as aioredis

from src.core.config import settings



class RedisClient:
    _instance: 'RedisClient | None' = None
    _pool: aioredis.Redis | None = None

    def __new__(cls) -> 'RedisClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        self._pool = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        logger.info('Redis connected')

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info('Redis disconnected')

    @property
    def pool(self) -> aioredis.Redis:
        if not self._pool:
            raise RuntimeError('Redis not connected')
        return self._pool

    async def save_verification_code(self, email: str, code: str) -> None:
        await self.pool.setex(f'verify:{email}', settings.VERIFY_CODE_TTL, code)
        logger.info('Verification code saved: email=%s', email)

    async def get_verification_code(self, email: str) -> str | None:
        return await self.pool.get(f'verify:{email}')

    async def delete_verification_code(self, email: str) -> None:
        await self.pool.delete(f'verify:{email}')
