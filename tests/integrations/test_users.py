import pytest

from src.modules.users.models import User, UserStatus


@pytest.mark.asyncio
async def test_get_user_by_id(restaurant_client):
    client, user = restaurant_client
    response = await client.get(f'/api/users/{user.id}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == user.name
    assert 'email' not in data


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    response = await client.get('/api/users/00000000-0000-0000-0000-000000000000')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_me(restaurant_client):
    client, user = restaurant_client
    response = await client.patch('/api/users/me', json={'name': 'New Name'})
    assert response.status_code == 200
    assert response.json()['name'] == 'New Name'

    db_user = await User.get(id=user.id)
    assert db_user.name == 'New Name'


@pytest.mark.asyncio
async def test_update_email(restaurant_client):
    client, user = restaurant_client
    response = await client.patch('/api/users/me', json={'email': 'new@test.com'})
    assert response.status_code == 200
    assert response.json()['email'] == 'new@test.com'

    db_user = await User.get(id=user.id)
    assert db_user.email == 'new@test.com'


@pytest.mark.asyncio
async def test_update_phone(restaurant_client):
    client, user = restaurant_client
    response = await client.patch('/api/users/me', json={'phone_number': '+70000000000'})
    assert response.status_code == 200
    assert response.json()['phone_number'] == '+70000000000'

    db_user = await User.get(id=user.id)
    assert db_user.phone_number == '+70000000000'


@pytest.mark.asyncio
async def test_update_duplicate_email(restaurant_client, farmer_user):
    client, _ = restaurant_client
    response = await client.patch('/api/users/me', json={'email': farmer_user.email})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_duplicate_phone(restaurant_client, farmer_user):
    client, _ = restaurant_client
    response = await client.patch('/api/users/me', json={'phone_number': farmer_user.phone_number})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_me_no_auth(client):
    response = await client.patch('/api/users/me', json={'name': 'New Name'})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_soft_delete(restaurant_client):
    client, user = restaurant_client
    response = await client.post('/api/users/me/delete')
    assert response.status_code == 204

    db_user = await User.get(id=user.id)
    assert db_user.status == UserStatus.DELETED
    assert '_deleted_' in db_user.email
    assert '_deleted_' in db_user.phone_number


@pytest.mark.asyncio
async def test_register_after_delete(client, register_payload):
    reg = await client.post('/api/auth/register', json=register_payload)
    token = reg.json()['access_token']
    await client.post('/api/users/me/delete', headers={'Authorization': f'Bearer {token}'})

    response = await client.post('/api/auth/register', json=register_payload)
    assert response.status_code == 201
