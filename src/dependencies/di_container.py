from dependency_injector import containers, providers

from src.clients.s3 import S3Client
from src.clients.smtp import SmtpClient
from src.domain.facade import Facade
from src.domain.repositories.offer_repo import OfferRepository
from src.domain.repositories.reservation_repo import ReservationRepository
from src.domain.repositories.review_repo import ReviewRepository
from src.domain.repositories.user_repo import UserRepository
from src.domain.services.auth_service import AuthService
from src.domain.services.feed_service import FeedService
from src.domain.services.offer_service import OfferService
from src.domain.services.payment_service import PaymentService
from src.domain.services.reservation_service import ReservationService
from src.domain.services.review_service import ReviewService
from src.domain.services.user_service import UserService
from src.producer.event_sender import EventSender
from src.cache import RedisClient


class DIContainer(containers.DeclarativeContainer):

    # --- Clients ---

    redis_client = providers.Singleton(RedisClient)
    s3_client = providers.Singleton(S3Client)
    smtp_client = providers.Singleton(SmtpClient)

    # --- Producer ---

    event_sender = providers.Singleton(EventSender)

    # --- Repositories ---

    user_repo = providers.Singleton(UserRepository)
    offer_repo = providers.Singleton(OfferRepository)
    reservation_repo = providers.Singleton(ReservationRepository)
    review_repo = providers.Singleton(ReviewRepository)

    # --- Services ---

    auth_service = providers.Singleton(
        AuthService,
        user_repo=user_repo,
        event_sender=event_sender,
        redis_client=redis_client,
    )

    user_service = providers.Singleton(
        UserService,
        user_repo=user_repo,
    )

    offer_service = providers.Singleton(
        OfferService,
        offer_repo=offer_repo,
    )

    feed_service = providers.Singleton(
        FeedService,
        offer_repo=offer_repo,
    )

    reservation_service = providers.Singleton(
        ReservationService,
        reservation_repo=reservation_repo,
        offer_repo=offer_repo,
        user_repo=user_repo,
        event_sender=event_sender,
    )

    review_service = providers.Singleton(
        ReviewService,
        review_repo=review_repo,
        reservation_repo=reservation_repo,
        offer_repo=offer_repo,
        user_repo=user_repo,
        event_sender=event_sender,
    )

    payment_service = providers.Singleton(
        PaymentService,
        reservation_repo=reservation_repo,
    )

    # --- Facade ---

    facade = providers.Singleton(
        Facade,
        auth_service=auth_service,
        user_service=user_service,
        offer_service=offer_service,
        feed_service=feed_service,
        reservation_service=reservation_service,
        review_service=review_service,
        payment_service=payment_service,
        smtp_client=smtp_client,
        redis_client=redis_client,
    )
