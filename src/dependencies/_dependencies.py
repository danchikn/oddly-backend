from src.clients.s3 import S3Client
from src.dependencies.di_container import DIContainer
from src.domain.facade import Facade
from src.cache import RedisClient

_container = DIContainer()


def get_facade() -> Facade:
    return _container.facade()


def get_redis_client() -> RedisClient:
    return _container.redis_client()


def get_s3_client() -> S3Client:
    return _container.s3_client()
