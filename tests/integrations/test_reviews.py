from tests.support.factories import OfferFactory, ReservationFactory


async def test_create_review(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status='COMPLETED')
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer, status='COMPLETED')
    response = await client.post('/api/v1/reviews', json={
        'reservation_id': str(reservation.id),
        'rating': 5,
        'comment': 'Great food!',
    })
    assert response.status_code == 201
    data = response.json()
    assert data['rating'] == 5
    assert data['target_id'] == str(restaurant_user.id)


async def test_create_review_not_completed(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer, status='ACTIVE')
    response = await client.post('/api/v1/reviews', json={
        'reservation_id': str(reservation.id),
        'rating': 5,
    })
    assert response.status_code == 400


async def test_duplicate_review(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status='COMPLETED')
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer, status='COMPLETED')
    await client.post('/api/v1/reviews', json={'reservation_id': str(reservation.id), 'rating': 4})
    response = await client.post('/api/v1/reviews', json={'reservation_id': str(reservation.id), 'rating': 5})
    assert response.status_code == 400


async def test_get_user_reviews(client, farmer_client, restaurant_user):
    c, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status='COMPLETED')
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer, status='COMPLETED')
    await c.post('/api/v1/reviews', json={'reservation_id': str(reservation.id), 'rating': 4, 'comment': 'Nice'})
    response = await client.get(f'/api/v1/reviews/user/{restaurant_user.id}')
    assert response.status_code == 200
    data = response.json()
    assert data['total_reviews'] == 1
    assert data['average_rating'] == 4.0
