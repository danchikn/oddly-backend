import pytest
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

from src.main import app
from tests.support.auth import make_auth_header
from tests.support.factories import UserFactory

TEST_DB_URL = 'asyncpg://postgres:postgres@localhost:5433/eco-feed-test'

TORTOISE_TEST_CONFIG = {
    'connections': {
        'default': TEST_DB_URL,
    },
    'apps': {
        'models': {
            'models': ['src.modules.users.models', 'src.modules.offers.models'],
            'default_connection': 'default',
        },
    },
}


@pytest.fixture(autouse=True)
async def db():
    await Tortoise.init(config=TORTOISE_TEST_CONFIG)
    await Tortoise.generate_schemas()
    yield
    conn = Tortoise.get_connection('default')
    tables = await conn.execute_query_dict(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
    )
    for t in tables:
        await conn.execute_query(f'TRUNCATE TABLE "{t["tablename"]}" CASCADE')
    await Tortoise.close_connections()


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
    from src.modules.users.models import UserRole
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
