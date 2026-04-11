import enum

from tortoise import fields
from tortoise.models import Model


class ReservationStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'


class Reservation(Model):
    id = fields.UUIDField(pk=True)
    offer = fields.ForeignKeyField('models.Offer', related_name='reservations')
    farmer = fields.ForeignKeyField('models.User', related_name='reservations')
    status = fields.CharEnumField(ReservationStatus, default=ReservationStatus.ACTIVE)
    payment_status = fields.CharField(max_length=20, default='UNPAID')  # UNPAID | PAID
    stripe_session_id = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'reservations'
        indexes = [
            ('farmer_id', 'created_at'),
            ('offer_id',),
        ]
