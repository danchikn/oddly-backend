import pytest


@pytest.mark.asyncio
async def test_register_success(client, register_payload):
    response = await client.post('/api/auth/register', json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert 'access_token' in data
    assert data['user']['email'] == register_payload['email']
    assert data['user']['role'] == register_payload['role']


@pytest.mark.asyncio
async def test_register_duplicate_email(client, register_payload):
    await client.post('/api/auth/register', json=register_payload)
    response = await client.post('/api/auth/register', json=register_payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_with_email(client, register_payload):
    await client.post('/api/auth/register', json=register_payload)
    response = await client.post('/api/auth/login', json={
        'identifier': register_payload['email'],
        'password': register_payload['password'],
    })
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['user']['email'] == register_payload['email']


@pytest.mark.asyncio
async def test_login_with_phone(client, register_payload):
    await client.post('/api/auth/register', json=register_payload)
    response = await client.post('/api/auth/login', json={
        'identifier': register_payload['phone_number'],
        'password': register_payload['password'],
    })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_wrong_password(client, register_payload):
    await client.post('/api/auth/register', json=register_payload)
    response = await client.post('/api/auth/login', json={
        'identifier': register_payload['email'],
        'password': 'wrongpassword',
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_success(restaurant_client):
    client, user = restaurant_client
    response = await client.get('/api/auth/me')
    assert response.status_code == 200
    assert response.json()['email'] == user.email


@pytest.mark.asyncio
async def test_login_deleted_user(restaurant_client):
    client, user = restaurant_client
    await client.post('/api/users/me/delete')
    response = await client.post('/api/auth/login', json={
        'identifier': user.email,
        'password': 'testpass123',
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_no_token(client):
    response = await client.get('/api/auth/me')
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client):
    response = await client.get('/api/auth/me', headers={'Authorization': 'Bearer garbage'})
    assert response.status_code == 401
