from tests.support.factories import OfferFactory, ReservationFactory


async def test_create_reservation(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user)
    response = await client.post('/api/v1/reservations', json={'offer_id': str(offer.id)})
    assert response.status_code == 201
    assert response.json()['status'] == 'ACTIVE'


async def test_create_reservation_not_farmer(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user)
    response = await client.post('/api/v1/reservations', json={'offer_id': str(offer.id)})
    assert response.status_code == 403


async def test_cancel_reservation(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer)
    response = await client.post(f'/api/v1/reservations/{reservation.id}/cancel')
    assert response.status_code == 200
    assert response.json()['status'] == 'CANCELLED'


async def test_complete_reservation(restaurant_client, farmer_user):
    client, owner = restaurant_client
    offer = await OfferFactory.create(owner=owner, status='RESERVED')
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer_user)
    response = await client.post(f'/api/v1/reservations/{reservation.id}/complete')
    assert response.status_code == 200
    assert response.json()['status'] == 'COMPLETED'


async def test_get_my_reservations(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user)
    await ReservationFactory.create(offer=offer, farmer=farmer)
    response = await client.get('/api/v1/reservations/my')
    assert response.status_code == 200
    assert response.json()['total'] == 1
