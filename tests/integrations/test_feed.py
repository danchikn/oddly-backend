from tests.support.factories import OfferFactory


async def test_feed_returns_open_offers(client, restaurant_user):
    await OfferFactory.create(owner=restaurant_user, status='OPEN')
    await OfferFactory.create(owner=restaurant_user, status='CANCELLED')
    response = await client.get('/api/v1/feed')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 1
    assert data['items'][0]['status'] == 'OPEN'


async def test_feed_with_geo(client, restaurant_user):
    await OfferFactory.create(owner=restaurant_user, latitude=41.30, longitude=69.24)
    response = await client.get('/api/v1/feed?lat=41.30&lng=69.24')
    assert response.status_code == 200
    assert response.json()['total'] >= 1


async def test_feed_empty(client):
    response = await client.get('/api/v1/feed')
    assert response.status_code == 200
    assert response.json()['total'] == 0
