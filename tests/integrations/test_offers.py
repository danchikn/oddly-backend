import pytest

from src.modules.offers.models import Offer, OfferStatus
from tests.support.factories import OfferFactory


@pytest.mark.asyncio
async def test_create_offer(restaurant_client):
    client, _ = restaurant_client
    payload = OfferFactory.build_payload()
    response = await client.post('/api/offers', json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data['description'] == payload['description']
    assert data['status'] == 'OPEN'

    db_offer = await Offer.get(id=data['id'])
    assert db_offer.description == payload['description']


@pytest.mark.asyncio
async def test_create_offer_no_auth(client):
    response = await client.post('/api/offers', json=OfferFactory.build_payload())
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_offer_by_id(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user)
    response = await client.get(f'/api/offers/{offer.id}')
    assert response.status_code == 200
    assert response.json()['id'] == str(offer.id)


@pytest.mark.asyncio
async def test_get_offer_not_found(client):
    response = await client.get('/api/offers/00000000-0000-0000-0000-000000000000')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_offer(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user)
    response = await client.patch(f'/api/offers/{offer.id}', json={'description': 'Updated'})
    assert response.status_code == 200
    assert response.json()['description'] == 'Updated'

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.description == 'Updated'


@pytest.mark.asyncio
async def test_update_offer_not_owner(farmer_client, restaurant_user):
    client, _ = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user)
    response = await client.patch(f'/api/offers/{offer.id}', json={'description': 'Hacked'})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_completed_offer(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user, status=OfferStatus.COMPLETED)
    response = await client.patch(f'/api/offers/{offer.id}', json={'description': 'Updated'})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_cancel_offer(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user)
    response = await client.post(f'/api/offers/{offer.id}/cancel')
    assert response.status_code == 200
    assert response.json()['status'] == 'CANCELLED'

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.CANCELLED


@pytest.mark.asyncio
async def test_cancel_offer_not_owner(farmer_client, restaurant_user):
    client, _ = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user)
    response = await client.post(f'/api/offers/{offer.id}/cancel')
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_cancel_completed_offer(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user, status=OfferStatus.COMPLETED)
    response = await client.post(f'/api/offers/{offer.id}/cancel')
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_my_offers(restaurant_client):
    client, user = restaurant_client
    await OfferFactory.create(owner=user)
    await OfferFactory.create(owner=user)
    await OfferFactory.create(owner=user, status=OfferStatus.COMPLETED)
    response = await client.get('/api/offers/my')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 3
    assert len(data['items']) == 3


@pytest.mark.asyncio
async def test_my_offers_filter_by_status(restaurant_client):
    client, user = restaurant_client
    await OfferFactory.create(owner=user)
    await OfferFactory.create(owner=user, status=OfferStatus.COMPLETED)
    response = await client.get('/api/offers/my?status=OPEN')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 1
    assert data['items'][0]['status'] == 'OPEN'


@pytest.mark.asyncio
async def test_my_offers_pagination(restaurant_client):
    client, user = restaurant_client
    for _ in range(5):
        await OfferFactory.create(owner=user)
    response = await client.get('/api/offers/my?page=1&limit=2')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 5
    assert len(data['items']) == 2
