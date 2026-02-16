import uuid

from src.modules.auth.service import hash_password
from src.modules.offers.models import Offer, OfferStatus
from src.modules.reservations.models import Reservation, ReservationStatus
from src.modules.users.models import User, UserRole, UserStatus


def _random_email() -> str:
    return f'user-{uuid.uuid4().hex[:8]}@test.com'


def _random_phone() -> str:
    return f'+7700{uuid.uuid4().int % 10_000_000:07d}'


class UserFactory:
    @staticmethod
    def build_payload(**overrides) -> dict:
        defaults = {
            'email': _random_email(),
            'phone_number': _random_phone(),
            'role': 'RESTAURANT',
            'name': 'Test User',
            'password': 'testpass123',
        }
        return {**defaults, **overrides}

    @staticmethod
    async def create(
        role: UserRole = UserRole.RESTAURANT,
        status: UserStatus = UserStatus.ACTIVE,
        password: str = 'testpass123',
        **overrides,
    ) -> User:
        defaults = {
            'email': _random_email(),
            'phone_number': _random_phone(),
            'role': role,
            'name': 'Test User',
            'password_hash': hash_password(password),
            'status': status,
        }
        return await User.create(**{**defaults, **overrides})


class OfferFactory:
    @staticmethod
    def build_payload(**overrides) -> dict:
        defaults = {
            'description': 'Fresh food waste available',
            'location_url': 'https://maps.google.com/test',
            'photos': [],
        }
        return {**defaults, **overrides}

    @staticmethod
    async def create(owner: User, status: OfferStatus = OfferStatus.OPEN, **overrides) -> Offer:
        defaults = {
            'owner': owner,
            'status': status,
            'description': 'Fresh food waste available',
            'location_url': 'https://maps.google.com/test',
            'photos': [],
        }
        return await Offer.create(**{**defaults, **overrides})


class ReservationFactory:
    @staticmethod
    async def create(
        offer: Offer,
        farmer: User,
        status: ReservationStatus = ReservationStatus.ACTIVE,
        **overrides,
    ) -> Reservation:
        defaults = {
            'offer': offer,
            'farmer': farmer,
            'status': status,
        }
        return await Reservation.create(**{**defaults, **overrides})
