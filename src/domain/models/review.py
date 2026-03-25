from tortoise import fields
from tortoise.models import Model


class Review(Model):
    id = fields.UUIDField(pk=True)
    reservation = fields.ForeignKeyField('models.Reservation', related_name='reviews')
    author = fields.ForeignKeyField('models.User', related_name='reviews_written')
    target = fields.ForeignKeyField('models.User', related_name='reviews_received')
    rating = fields.SmallIntField()
    comment = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'reviews'
        unique_together = (('reservation', 'author'),)
        indexes = [
            ('target_id', 'created_at'),
        ]
