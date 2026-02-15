import enum

from tortoise import fields
from tortoise.models import Model


class OfferStatus(str, enum.Enum):
    OPEN = 'OPEN'
    RESERVED = 'RESERVED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'


class Offer(Model):
    id = fields.UUIDField(pk=True)
    owner = fields.ForeignKeyField('models.User', related_name='offers')
    status = fields.CharEnumField(OfferStatus, default=OfferStatus.OPEN)
    description = fields.TextField()
    pickup_from = fields.DatetimeField(null=True)
    pickup_to = fields.DatetimeField(null=True)
    location_url = fields.TextField()
    photos = fields.JSONField(default=list, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'offers'
        indexes = [
            ('status', 'created_at'),
            ('owner_id', 'created_at'),
        ]
