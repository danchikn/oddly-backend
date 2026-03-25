from src.worker.schemas import NotificationEvent


async def notification_handler(data: NotificationEvent) -> None:
    from src.dependencies import get_facade
    await get_facade().handle_notification(data)
