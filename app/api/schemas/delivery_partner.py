from pydantic import BaseModel, EmailStr, Field

from app.database.models import Location

class BaseDeliveryPartner(BaseModel):
    name: str
    email: EmailStr
    max_handling_capacity: int


class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str
    servicable_zip_codes: list[int]

class DeliveryPartnerRead(BaseDeliveryPartner):
    servicable_locations:list[Location]

class DeliveryPartnerUpdate(BaseModel):
    servicable_zip_codes: list[int]| None
    max_handling_capacity: int | None =Field(default=None)