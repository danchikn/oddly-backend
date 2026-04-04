from typing import Any

from faststream.rabbit import RabbitBroker
from loguru import logger

from src.core.config import settings


class Producer:
    """RabbitMQ message producer singleton for publishing messages to exchanges. YES"""

    _instance = None
    _initialized = False

    def __new__(cls) -> 'Producer':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._broker = RabbitBroker(url=str(settings.RABBITMQ_URL))
            self._connected = False
            self._initialized = True

    async def connect(self) -> None:
        """Connect to RabbitMQ broker."""
        if self._broker is None:
            self._broker = RabbitBroker(url=str(settings.RABBITMQ_URL))
        await self._broker.connect()
        self._connected = True

    async def close(self) -> None:
        """Close connection to RabbitMQ broker."""
        if self._broker:
            await self._broker.stop()
            self._broker = None
        self._connected = False
        self._initialized = False

    async def publish(
        self,
        exchange: str,
        routing_key: str,
        message: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> None:
        """Publish message to specified exchange with routing key.

        Args:
            exchange: The exchange to publish the message to.
            routing_key: The routing key to use for the message.
            message: The message to publish.
            headers: Optional AMQP message headers.
        """
        await self._broker.publish(
            exchange=exchange,
            routing_key=routing_key,
            message=message,
            headers=headers,
        )

    @property
    def is_connected(self) -> bool:
        """Check if the producer is connected to RabbitMQ."""
        return self._connected


async def producer_connect() -> None:
    """Connect the singleton producer instance to RabbitMQ."""
    logger.info('Connecting to RabbitMQ broker')
    await Producer().connect()


async def producer_disconnect() -> None:
    """Disconnect the singleton producer instance from RabbitMQ."""
    logger.info('Disconnecting from RabbitMQ broker')
    await Producer().close()
