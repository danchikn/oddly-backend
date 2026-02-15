import pytest

from src.modules.offers.models import OfferStatus
from tests.support.factories import OfferFactory, UserFactory


@pytest.mark.asyncio
async def test_feed_returns_only_open(client):
    owner = await UserFactory.create()
    await OfferFactory.create(owner=owner, status=OfferStatus.OPEN)
    await OfferFactory.create(owner=owner, status=OfferStatus.OPEN)
    await OfferFactory.create(owner=owner, status=OfferStatus.RESERVED)
    await OfferFactory.create(owner=owner, status=OfferStatus.COMPLETED)
    await OfferFactory.create(owner=owner, status=OfferStatus.CANCELLED)

    response = await client.get('/api/feed')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 2
    for item in data['items']:
        assert item['status'] == 'OPEN'


@pytest.mark.asyncio
async def test_feed_pagination(client):
    owner = await UserFactory.create()
    for _ in range(5):
        await OfferFactory.create(owner=owner)

    response = await client.get('/api/feed?page=1&limit=2')
    data = response.json()
    assert data['total'] == 5
    assert len(data['items']) == 2

    response = await client.get('/api/feed?page=3&limit=2')
    data = response.json()
    assert len(data['items']) == 1


@pytest.mark.asyncio
async def test_feed_ordered_by_newest(client):
    owner = await UserFactory.create()
    first = await OfferFactory.create(owner=owner, description='first')
    second = await OfferFactory.create(owner=owner, description='second')

    response = await client.get('/api/feed')
    items = response.json()['items']
    assert items[0]['id'] == str(second.id)
    assert items[1]['id'] == str(first.id)


@pytest.mark.asyncio
async def test_feed_empty(client):
    response = await client.get('/api/feed')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 0
    assert data['items'] == []
