from uuid import UUID

from src.domain.models.user import User, UserStatus


class UserRepository:
    async def get_by_id(self, user_id: UUID) -> User | None:
        return await User.filter(id=user_id).first()

    async def get_active_by_id(self, user_id: UUID) -> User | None:
        return await User.filter(id=user_id, status=UserStatus.ACTIVE).first()

    async def get_by_email(self, email: str) -> User | None:
        return await User.filter(email=email).first()

    async def get_by_phone(self, phone: str) -> User | None:
        return await User.filter(phone_number=phone).first()

    async def get_unverified_by_email(self, email: str) -> User | None:
        return await User.filter(email=email, status=UserStatus.UNVERIFIED).first()

    async def exists_by_email(self, email: str) -> bool:
        return await User.filter(email=email).exists()

    async def exists_by_phone(self, phone: str) -> bool:
        return await User.filter(phone_number=phone).exists()

    async def create(self, **kwargs) -> User:
        return await User.create(**kwargs)

    async def save(self, user: User) -> None:
        await user.save()

    async def mark_active(self, user: User) -> None:
        user.status = UserStatus.ACTIVE
        await user.save()

    async def mark_deleted(self, user: User, suffix: str) -> None:
        user.status = UserStatus.DELETED
        user.email = user.email + suffix
        user.phone_number = user.phone_number + suffix
        await user.save()
