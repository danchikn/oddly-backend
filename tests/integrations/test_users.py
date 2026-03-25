async def test_get_user_profile(client, restaurant_user):
    response = await client.get(f'/api/v1/users/{restaurant_user.id}')
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == str(restaurant_user.id)
    assert 'email' not in data


async def test_update_me(restaurant_client):
    client, user = restaurant_client
    response = await client.patch('/api/v1/users/me', json={'name': 'Updated Name'})
    assert response.status_code == 200
    assert response.json()['name'] == 'Updated Name'


async def test_delete_me(restaurant_client):
    client, user = restaurant_client
    response = await client.post('/api/v1/users/me/delete')
    assert response.status_code == 204
