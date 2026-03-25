import pytest

from tests.support.factories import UserFactory


async def test_register(client, register_payload):
    response = await client.post('/api/v1/auth/register', json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert 'access_token' in data
    assert data['user']['email'] == register_payload['email']
    assert data['user']['status'] == 'UNVERIFIED'


async def test_register_duplicate_email(client, register_payload):
    await client.post('/api/v1/auth/register', json=register_payload)
    response = await client.post('/api/v1/auth/register', json=register_payload)
    assert response.status_code == 409


async def test_login(client, restaurant_user):
    response = await client.post('/api/v1/auth/login', json={
        'identifier': restaurant_user.email,
        'password': 'testpass123',
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()


async def test_login_wrong_password(client, restaurant_user):
    response = await client.post('/api/v1/auth/login', json={
        'identifier': restaurant_user.email,
        'password': 'wrongpassword',
    })
    assert response.status_code == 401


async def test_login_unverified(client):
    user = await UserFactory.create(status='UNVERIFIED')
    response = await client.post('/api/v1/auth/login', json={
        'identifier': user.email,
        'password': 'testpass123',
    })
    assert response.status_code == 401
    assert 'verified' in response.json()['detail'].lower()


async def test_me(restaurant_client):
    client, user = restaurant_client
    response = await client.get('/api/v1/auth/me')
    assert response.status_code == 200
    assert response.json()['id'] == str(user.id)


async def test_me_unauthorized(client):
    response = await client.get('/api/v1/auth/me')
    assert response.status_code in (401, 403)
