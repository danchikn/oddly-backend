from uuid import UUID

from src.domain.models.reservation import Reservation, ReservationStatus


class ReservationRepository:
    async def get_by_id(self, reservation_id: UUID) -> Reservation | None:
        return await Reservation.filter(id=reservation_id).first()

    async def create(self, **kwargs) -> Reservation:
        return await Reservation.create(**kwargs)

    async def save(self, reservation: Reservation) -> None:
        await reservation.save()

    async def mark_cancelled(self, reservation: Reservation) -> None:
        reservation.status = ReservationStatus.CANCELLED
        await reservation.save()

    async def mark_completed(self, reservation: Reservation) -> None:
        reservation.status = ReservationStatus.COMPLETED
        await reservation.save()

    async def get_by_farmer(
        self,
        farmer_id: UUID,
        status: ReservationStatus | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Reservation], int]:
        query = Reservation.filter(farmer_id=farmer_id)
        if status:
            query = query.filter(status=status)
        total = await query.count()
        items = await query.order_by('-created_at').offset((page - 1) * limit).limit(limit)
        return items, total

    async def get_incoming(
        self,
        owner_id: UUID,
        status: ReservationStatus | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Reservation], int]:
        query = Reservation.filter(offer__owner_id=owner_id)
        if status:
            query = query.filter(status=status)
        total = await query.count()
        items = await query.order_by('-created_at').offset((page - 1) * limit).limit(limit)
        return items, total
