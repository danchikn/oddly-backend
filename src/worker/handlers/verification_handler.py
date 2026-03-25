from src.worker.schemas import VerificationEvent


async def verification_handler(data: VerificationEvent) -> None:
    from src.dependencies import get_facade
    await get_facade().handle_verification(data)
