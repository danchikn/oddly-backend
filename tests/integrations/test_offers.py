from tests.support.factories import OfferFactory


async def test_create_offer(restaurant_client):
    client, user = restaurant_client
    response = await client.post('/api/v1/offers', json={
        'description': 'Fresh vegetables',
        'location_url': 'https://maps.google.com/?q=41.29,69.24',
    })
    assert response.status_code == 201
    data = response.json()
    assert data['description'] == 'Fresh vegetables'
    assert data['status'] == 'OPEN'


async def test_get_offer(client, restaurant_user):
    offer = await OfferFactory.create(owner=restaurant_user)
    response = await client.get(f'/api/v1/offers/{offer.id}')
    assert response.status_code == 200
    assert response.json()['id'] == str(offer.id)


async def test_get_my_offers(restaurant_client):
    client, user = restaurant_client
    await OfferFactory.create(owner=user)
    await OfferFactory.create(owner=user)
    response = await client.get('/api/v1/offers/my')
    assert response.status_code == 200
    assert response.json()['total'] == 2


async def test_update_offer(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user)
    response = await client.patch(f'/api/v1/offers/{offer.id}', json={'description': 'Updated'})
    assert response.status_code == 200
    assert response.json()['description'] == 'Updated'


async def test_cancel_offer(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user)
    response = await client.post(f'/api/v1/offers/{offer.id}/cancel')
    assert response.status_code == 200
    assert response.json()['status'] == 'CANCELLED'


async def test_cancel_already_cancelled(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user, status='CANCELLED')
    response = await client.post(f'/api/v1/offers/{offer.id}/cancel')
    assert response.status_code == 400
