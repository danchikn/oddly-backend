from pydantic import BaseModel


class VerificationEvent(BaseModel):
    user_id: str
    email: str
    name: str


class NotificationEvent(BaseModel):
    type: str
    recipient_email: str
    recipient_name: str
    farmer_name: str | None = None
    owner_name: str | None = None
    offer_description: str | None = None
