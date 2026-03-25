from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer
from tortoise import Tortoise

from src.core.rate_limit import limiter
from src.start_web import app
from tests.support.auth import make_auth_header
from tests.support.factories import UserFactory

limiter.enabled = False

MODELS = [
    'src.domain.models.user',
    'src.domain.models.offer',
    'src.domain.models.reservation',
    'src.domain.models.review',
]


@pytest.fixture(scope='session')
def postgres_url():
    with PostgresContainer('postgres:16-alpine') as pg:
        url = pg.get_connection_url().replace('postgresql+psycopg2://', 'asyncpg://')
        yield url


@pytest.fixture(autouse=True)
async def db(postgres_url):
    config = {
        'connections': {'default': postgres_url},
        'apps': {
            'models': {
                'models': MODELS,
                'default_connection': 'default',
            },
        },
    }
    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()
    yield
    conn = Tortoise.get_connection('default')
    tables = await conn.execute_query_dict(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
    )
    for t in tables:
        await conn.execute_query(f'TRUNCATE TABLE "{t["tablename"]}" CASCADE')
    await Tortoise.close_connections()


@pytest.fixture(autouse=True)
def mock_event_sender():
    with patch('src.producer.event_sender.EventSender.send_verification', new_callable=AsyncMock) as mock_verify, \
         patch('src.producer.event_sender.EventSender.send_notification', new_callable=AsyncMock) as mock_notify:
        yield {'send_verification': mock_verify, 'send_notification': mock_notify}


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture
def register_payload():
    return UserFactory.build_payload()


@pytest.fixture
async def restaurant_user():
    return await UserFactory.create()


@pytest.fixture
async def farmer_user():
    from src.domain.models.user import UserRole
    return await UserFactory.create(role=UserRole.FARMER)


@pytest.fixture
async def auth_header(restaurant_user):
    return make_auth_header(restaurant_user)


@pytest.fixture
async def restaurant_client(client, restaurant_user):
    headers = make_auth_header(restaurant_user)
    client.headers.update(headers)
    yield client, restaurant_user


@pytest.fixture
async def farmer_client(client, farmer_user):
    headers = make_auth_header(farmer_user)
    client.headers.update(headers)
    yield client, farmer_user
