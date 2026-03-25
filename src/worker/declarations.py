from faststream.rabbit import (
    ExchangeType,
    QueueType,
    RabbitExchange,
    RabbitQueue,
    RabbitRoute,
    RabbitRouter,
)

from src.constants import NOTIFICATION_ROUTING_KEY, ODDLY_EXCHANGE, VERIFY_ROUTING_KEY
from src.worker.handlers import notification_handler, verification_handler

oddly_x = RabbitExchange(name=ODDLY_EXCHANGE, type=ExchangeType.TOPIC, durable=True)

notification_q = RabbitQueue(
    name=f'oddly_{NOTIFICATION_ROUTING_KEY}_q',
    routing_key=NOTIFICATION_ROUTING_KEY,
    durable=True, queue_type=QueueType.QUORUM,
)

verification_q = RabbitQueue(
    name=f'oddly_{VERIFY_ROUTING_KEY}_q',
    routing_key=VERIFY_ROUTING_KEY,
    durable=True, queue_type=QueueType.QUORUM,
)

event_router = RabbitRouter(handlers=[
    RabbitRoute(call=notification_handler, exchange=oddly_x, queue=notification_q),
    RabbitRoute(call=verification_handler, exchange=oddly_x, queue=verification_q),
])
