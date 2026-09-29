from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme_seller=OAuth2PasswordBearer(tokenUrl="/seller/login", scheme_name="SellerAuth")

oauth2_scheme_partner=OAuth2PasswordBearer(tokenUrl="/partner/login", scheme_name="PartnerAuth")

class TokenData(BaseModel):
    access_token:str
    token_type:str