import asyncio
from loguru import logger
from datetime import datetime, timedelta, timezone

from tortoise import Tortoise

from src.db import TORTOISE_ORM
import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
from src.domain.models.offer import Offer, OfferStatus
from src.domain.models.user import User, UserRole, UserStatus



RESTAURANT_LOCATION = 'https://maps.google.com/?q=41.2995,69.2401'

OFFERS_DATA = [
    {
        'description': 'Fresh vegetable mix — 5 kg of tomatoes, cucumbers, and bell peppers. '
        'Slightly imperfect shapes but great taste. Perfect for salads or cooking.',
        'location_url': RESTAURANT_LOCATION,
        'hours_from_now': 2,
        'hours_window': 4,
        # TODO: add photo URL later
    },
    {
        'description': 'Bakery surplus — 12 loaves of sourdough bread and 20 croissants baked this morning. '
        'Best consumed today.',
        'location_url': RESTAURANT_LOCATION,
        'hours_from_now': 1,
        'hours_window': 3,
        # TODO: add photo URL later
    },
    {
        'description': 'Dairy bundle — 3 L of whole milk, 2 kg of yogurt, and 500 g of feta cheese. '
        'Approaching best-before date (2 days left). All refrigerated.',
        'location_url': RESTAURANT_LOCATION,
        'hours_from_now': 3,
        'hours_window': 5,
        # TODO: add photo URL later
    },
    {
        'description': 'Cooked meals — 15 portions of plov (pilaf) and 10 portions of grilled chicken. '
        'Prepared today for a cancelled event. Containers provided.',
        'location_url': RESTAURANT_LOCATION,
        'hours_from_now': 0,
        'hours_window': 2,
        # TODO: add photo URL later
    },
    {
        'description': 'Fruit box — 8 kg of seasonal apples, pears, and grapes. '
        'Some cosmetic blemishes but perfectly edible. Great for juicing.',
        'location_url': RESTAURANT_LOCATION,
        'hours_from_now': 4,
        'hours_window': 6,
        # TODO: add photo URL later
    },
    {
        'description': 'Pastry assortment — 30 pieces including baklava, cookies, and muffins. '
        "From today's overproduction. Individually wrapped.",
        'location_url': RESTAURANT_LOCATION,
        'hours_from_now': 1,
        'hours_window': 4,
        # TODO: add photo URL later
    },
]


async def seed() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    # --- Users ---
    restaurant, created = await User.get_or_create(
        email='restaurant@oddly.com',
        defaults={
            'phone_number': '+7 777 777 77 77',
            'role': UserRole.RESTAURANT,
            'name': 'Green Kitchen',
            'password_hash': hash_password('Restaurant123'),
            'location_url': RESTAURANT_LOCATION,
            'status': UserStatus.ACTIVE,
        },
    )
    logger.info(
        '%s restaurant user: id=%s email=%s',
        'Created' if created else 'Found existing',
        restaurant.id,
        restaurant.email,
    )

    farmer, created = await User.get_or_create(
        email='farmer@oddly.com',
        defaults={
            'phone_number': '+7 777 777 77 78',
            'role': UserRole.FARMER,
            'name': 'Ali the Farmer',
            'password_hash': hash_password('Farmer123'),
            'status': UserStatus.ACTIVE,
        },
    )
    logger.info(
        '%s farmer user: id=%s email=%s',
        'Created' if created else 'Found existing',
        farmer.id,
        farmer.email,
    )

    # --- Offers (without photos — TODO: add photos later) ---
    existing_count = await Offer.filter(owner=restaurant).count()
    if existing_count >= len(OFFERS_DATA):
        logger.info('Offers already seeded (%d found), skipping', existing_count)
    else:
        now = datetime.now(timezone.utc)
        for data in OFFERS_DATA:
            await Offer.create(
                owner=restaurant,
                status=OfferStatus.OPEN,
                description=data['description'],
                location_url=data['location_url'],
                latitude=41.2995,
                longitude=69.2401,
                pickup_from=now + timedelta(hours=data['hours_from_now']),
                pickup_to=now + timedelta(hours=data['hours_from_now'] + data['hours_window']),
            )
        logger.info('Created %d offers', len(OFFERS_DATA))

    total_offers = await Offer.filter(owner=restaurant).count()
    logger.info('Total offers for restaurant: %d', total_offers)

    await Tortoise.close_connections()
    logger.info('Seed complete!')


if __name__ == '__main__':
    asyncio.run(seed())
