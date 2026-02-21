import enum

from tortoise import fields
from tortoise.models import Model


class UserRole(str, enum.Enum):
    RESTAURANT = 'RESTAURANT'
    FARMER = 'FARMER'


class UserStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    BLOCKED = 'BLOCKED'
    DELETED = 'DELETED'


class User(Model):
    id = fields.UUIDField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    phone_number = fields.CharField(max_length=40, unique=True)
    role = fields.CharEnumField(UserRole)
    name = fields.CharField(max_length=255, null=True)
    password_hash = fields.CharField(max_length=255)
    location_url = fields.TextField(null=True, default=None)
    status = fields.CharEnumField(UserStatus, default=UserStatus.ACTIVE)
    blocked_until = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'users'
