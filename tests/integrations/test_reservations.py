import pytest

from src.modules.offers.models import Offer, OfferStatus
from src.modules.reservations.models import Reservation, ReservationStatus
from tests.support.factories import OfferFactory, ReservationFactory, UserFactory


@pytest.mark.asyncio
async def test_create_reservation(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user)
    response = await client.post('/api/reservations', json={'offer_id': str(offer.id)})
    assert response.status_code == 201
    data = response.json()
    assert data['offer_id'] == str(offer.id)
    assert data['farmer_id'] == str(farmer.id)
    assert data['status'] == 'ACTIVE'

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.RESERVED


@pytest.mark.asyncio
async def test_create_reservation_not_farmer(restaurant_client):
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user)
    response = await client.post('/api/reservations', json={'offer_id': str(offer.id)})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_reservation_offer_not_open(farmer_client, restaurant_user):
    client, _ = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status=OfferStatus.RESERVED)
    response = await client.post('/api/reservations', json={'offer_id': str(offer.id)})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_reservation_offer_not_found(farmer_client):
    client, _ = farmer_client
    response = await client.post(
        '/api/reservations',
        json={'offer_id': '00000000-0000-0000-0000-000000000000'},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_reservation_no_auth(client, restaurant_user):
    offer = await OfferFactory.create(owner=restaurant_user)
    response = await client.post('/api/reservations', json={'offer_id': str(offer.id)})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_reservation_by_id(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer)
    response = await client.get(f'/api/reservations/{reservation.id}')
    assert response.status_code == 200
    assert response.json()['id'] == str(reservation.id)


@pytest.mark.asyncio
async def test_get_reservation_not_found(farmer_client):
    client, _ = farmer_client
    response = await client.get('/api/reservations/00000000-0000-0000-0000-000000000000')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_reservation_no_auth(client, farmer_user, restaurant_user):
    offer = await OfferFactory.create(owner=restaurant_user)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer_user)
    response = await client.get(f'/api/reservations/{reservation.id}')
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_reservation_not_participant(restaurant_user, farmer_user):
    """Пользователь, не являющийся участником бронирования, получает 403."""
    from httpx import ASGITransport, AsyncClient
    from src.main import app
    from tests.support.auth import make_auth_header

    other_user = await UserFactory.create()
    offer = await OfferFactory.create(owner=restaurant_user)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer_user)

    headers = make_auth_header(other_user)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test', headers=headers) as ac:
        response = await ac.get(f'/api/reservations/{reservation.id}')
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_reservation_by_offer_owner(restaurant_client, farmer_user):
    """Владелец оффера тоже может просмотреть бронирование."""
    client, restaurant = restaurant_client
    offer = await OfferFactory.create(owner=restaurant)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer_user)
    response = await client.get(f'/api/reservations/{reservation.id}')
    assert response.status_code == 200
    assert response.json()['id'] == str(reservation.id)


@pytest.mark.asyncio
async def test_cancel_reservation(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status=OfferStatus.RESERVED)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer)
    response = await client.post(f'/api/reservations/{reservation.id}/cancel')
    assert response.status_code == 200
    assert response.json()['status'] == 'CANCELLED'

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.OPEN

    db_reservation = await Reservation.get(id=reservation.id)
    assert db_reservation.status == ReservationStatus.CANCELLED


@pytest.mark.asyncio
async def test_cancel_reservation_not_owner(restaurant_client, farmer_user):
    client, restaurant = restaurant_client
    offer = await OfferFactory.create(owner=restaurant, status=OfferStatus.RESERVED)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer_user)
    response = await client.post(f'/api/reservations/{reservation.id}/cancel')
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_cancel_completed_reservation(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status=OfferStatus.COMPLETED)
    reservation = await ReservationFactory.create(
        offer=offer, farmer=farmer, status=ReservationStatus.COMPLETED
    )
    response = await client.post(f'/api/reservations/{reservation.id}/cancel')
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_complete_reservation(restaurant_client, farmer_user):
    client, restaurant = restaurant_client
    offer = await OfferFactory.create(owner=restaurant, status=OfferStatus.RESERVED)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer_user)
    response = await client.post(f'/api/reservations/{reservation.id}/complete')
    assert response.status_code == 200
    assert response.json()['status'] == 'COMPLETED'

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.COMPLETED

    db_reservation = await Reservation.get(id=reservation.id)
    assert db_reservation.status == ReservationStatus.COMPLETED


@pytest.mark.asyncio
async def test_complete_reservation_not_offer_owner(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status=OfferStatus.RESERVED)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer)
    response = await client.post(f'/api/reservations/{reservation.id}/complete')
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_complete_cancelled_reservation(restaurant_client, farmer_user):
    client, restaurant = restaurant_client
    offer = await OfferFactory.create(owner=restaurant, status=OfferStatus.RESERVED)
    reservation = await ReservationFactory.create(
        offer=offer, farmer=farmer_user, status=ReservationStatus.CANCELLED
    )
    response = await client.post(f'/api/reservations/{reservation.id}/complete')
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_my_reservations(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer1 = await OfferFactory.create(owner=restaurant_user)
    offer2 = await OfferFactory.create(owner=restaurant_user)
    await ReservationFactory.create(offer=offer1, farmer=farmer)
    await ReservationFactory.create(offer=offer2, farmer=farmer)
    response = await client.get('/api/reservations/my')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 2
    assert len(data['items']) == 2


@pytest.mark.asyncio
async def test_my_reservations_filter_by_status(farmer_client, restaurant_user):
    client, farmer = farmer_client
    offer1 = await OfferFactory.create(owner=restaurant_user)
    offer2 = await OfferFactory.create(owner=restaurant_user)
    await ReservationFactory.create(offer=offer1, farmer=farmer)
    await ReservationFactory.create(
        offer=offer2, farmer=farmer, status=ReservationStatus.CANCELLED
    )
    response = await client.get('/api/reservations/my?status=ACTIVE')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 1
    assert data['items'][0]['status'] == 'ACTIVE'


@pytest.mark.asyncio
async def test_my_reservations_pagination(farmer_client, restaurant_user):
    client, farmer = farmer_client
    for _ in range(5):
        offer = await OfferFactory.create(owner=restaurant_user)
        await ReservationFactory.create(offer=offer, farmer=farmer)
    response = await client.get('/api/reservations/my?page=1&limit=2')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 5
    assert len(data['items']) == 2


# --- Тесты на откат транзакции: при ошибке БД не должна измениться ---


@pytest.mark.asyncio
async def test_create_reservation_not_open_offer_stays_unchanged(farmer_client, restaurant_user):
    """Попытка забронировать RESERVED offer — offer остаётся RESERVED, reservation не создаётся."""
    client, _ = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status=OfferStatus.RESERVED)
    response = await client.post('/api/reservations', json={'offer_id': str(offer.id)})
    assert response.status_code == 400

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.RESERVED

    count = await Reservation.filter(offer_id=offer.id).count()
    assert count == 0


@pytest.mark.asyncio
async def test_create_reservation_restaurant_role_offer_stays_open(restaurant_client):
    """Ресторан пытается забронировать — offer остаётся OPEN, reservation не создаётся."""
    client, user = restaurant_client
    offer = await OfferFactory.create(owner=user)
    response = await client.post('/api/reservations', json={'offer_id': str(offer.id)})
    assert response.status_code == 403

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.OPEN

    count = await Reservation.filter(offer_id=offer.id).count()
    assert count == 0


@pytest.mark.asyncio
async def test_cancel_reservation_not_owner_db_unchanged(restaurant_client, farmer_user):
    """Не-владелец пытается отменить — reservation и offer не меняются."""
    client, restaurant = restaurant_client
    offer = await OfferFactory.create(owner=restaurant, status=OfferStatus.RESERVED)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer_user)
    response = await client.post(f'/api/reservations/{reservation.id}/cancel')
    assert response.status_code == 403

    db_reservation = await Reservation.get(id=reservation.id)
    assert db_reservation.status == ReservationStatus.ACTIVE

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.RESERVED


@pytest.mark.asyncio
async def test_cancel_completed_reservation_db_unchanged(farmer_client, restaurant_user):
    """Отмена завершённого бронирования — ничего не меняется."""
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status=OfferStatus.COMPLETED)
    reservation = await ReservationFactory.create(
        offer=offer, farmer=farmer, status=ReservationStatus.COMPLETED
    )
    response = await client.post(f'/api/reservations/{reservation.id}/cancel')
    assert response.status_code == 400

    db_reservation = await Reservation.get(id=reservation.id)
    assert db_reservation.status == ReservationStatus.COMPLETED

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.COMPLETED


@pytest.mark.asyncio
async def test_complete_reservation_not_offer_owner_db_unchanged(farmer_client, restaurant_user):
    """Фермер пытается завершить — reservation и offer не меняются."""
    client, farmer = farmer_client
    offer = await OfferFactory.create(owner=restaurant_user, status=OfferStatus.RESERVED)
    reservation = await ReservationFactory.create(offer=offer, farmer=farmer)
    response = await client.post(f'/api/reservations/{reservation.id}/complete')
    assert response.status_code == 403

    db_reservation = await Reservation.get(id=reservation.id)
    assert db_reservation.status == ReservationStatus.ACTIVE

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.RESERVED


@pytest.mark.asyncio
async def test_complete_cancelled_reservation_db_unchanged(restaurant_client, farmer_user):
    """Завершение отменённого бронирования — ничего не меняется."""
    client, restaurant = restaurant_client
    offer = await OfferFactory.create(owner=restaurant, status=OfferStatus.RESERVED)
    reservation = await ReservationFactory.create(
        offer=offer, farmer=farmer_user, status=ReservationStatus.CANCELLED
    )
    response = await client.post(f'/api/reservations/{reservation.id}/complete')
    assert response.status_code == 400

    db_reservation = await Reservation.get(id=reservation.id)
    assert db_reservation.status == ReservationStatus.CANCELLED

    db_offer = await Offer.get(id=offer.id)
    assert db_offer.status == OfferStatus.RESERVED
