from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from uuid import UUID

from app.database.models import ShipmentEvent, ShipmentStatus, Tag, TagName


class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    destination: int

class TagRead(BaseModel):
    name: TagName
    instruction: str

class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime
    tags: list[Tag]

class ShipmentCreate(BaseShipment):
    client_contact_email: EmailStr
    client_contact_phone: int | None=Field(default=None)

class ShipmentUpdate(BaseModel):
    location: int | None= Field(default=None)
    description: str | None= Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)

class ShipmentReview(BaseModel):
    rating: int=Field(ge=1, le=5)
    comment: str|None= Field(default=None)
