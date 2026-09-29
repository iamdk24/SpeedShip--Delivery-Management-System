from pydantic import BaseModel, EmailStr

class BaseSeller(BaseModel):
    name: str
    email: EmailStr


class SellerCreate(BaseSeller):
    password: str
    address: str
    zip_code:int

class SellerRead(BaseSeller):
    pass
    