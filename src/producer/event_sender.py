from typing import Any

from faststream.rabbit import RabbitExchange
from loguru import logger
from pydantic import BaseModel

from src.constants import NOTIFICATION_ROUTING_KEY, ODDLY_EXCHANGE, VERIFY_ROUTING_KEY
from src.producer._producer import Producer


class EventSender:
    def __init__(self) -> None:
        self._producer = Producer()

    async def _publish(
        self,
        exchange: str | RabbitExchange,
        routing_key: str,
        message: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> None:
        if not self._producer.is_connected:
            raise RuntimeError('Producer is not connected. Please call connect() first.')

        logger.info(
            'Publishing message to exchange: {exchange}, routing_key: {routing_key}',
            exchange=exchange,
            routing_key=routing_key,
        )

        try:
            await self._producer.publish(
                exchange=exchange,
                routing_key=routing_key,
                message=message,
                headers=headers,
            )
        except Exception as e:
            logger.error('Error while publishing message: {error}', error=e)
            raise

    async def _send(self, exchange: str, routing_key: str, event: BaseModel) -> None:
        await self._publish(exchange=exchange, routing_key=routing_key, message=event.model_dump(mode='json'))

    async def send_verification(self, data: dict[str, Any]) -> None:
        await self._publish(ODDLY_EXCHANGE, VERIFY_ROUTING_KEY, data)

    async def send_notification(self, data: dict[str, Any]) -> None:
        await self._publish(ODDLY_EXCHANGE, NOTIFICATION_ROUTING_KEY, data)
