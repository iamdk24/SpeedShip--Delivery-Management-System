from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request,status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.api.schemas.seller import SellerCreate, SellerRead
from app.api.dependencies import SellerDep, SellerServiceDep, SessionDep, get_seller_access_token
from app.api.schemas.shipment import ShipmentRead
from app.api.tag import ApiTag
from app.core.exceptions import InvalidToken
from app.core.security import TokenData, oauth2_scheme_seller
from app.database.models import Seller
from app.database.redis import add_jti_to_blacklist
from app.utils import TEMPLATE_DIR, decode_access_token
from app.config import app_settings

router=APIRouter(prefix="/seller", tags=[ApiTag.SELLER])


# Register a Seller
@router.post("/signup", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)

#Verify Seller Email
@router.get("/verify")
async def verify_seller_email(token:str, service: SellerServiceDep):
    await service.verify_email(token)
    return{"detail":"Account Verified"}

#Email Password reset link for Seller
@router.get("/forgot_password")
async def forgot_password(email: EmailStr, service: SellerServiceDep):
    await service.send_password_reset_link(email, router_prefix="seller")
    return{"detail":"Check Email for Password reset link"}

#Password Reset Form
@router.get("/reset_password_form")
async def get_reset_password_form(request:Request,token:str):
    templates=Jinja2Templates(TEMPLATE_DIR)

    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={"reset_url":f"https://{app_settings.APP_DOMAIN}/seller/reset_password?token={token}"}
    )

# Reset Seller Password
@router.post("/reset_password")
async def reset_password(token: str,password: Annotated[str,Form()], service: SellerServiceDep):
    await service.reset_password(token, password)
    return{"detail":"Password reset Successful"}



# Login the Seller
@router.post("/login",response_model=TokenData)
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep
    ):
    token = await service.token(request_form.username, request_form.password)
    return{
        "access_token": token,
        "token_type": "bearer"
    }

### Get Seller Profile
@router.get("/me", response_model=SellerRead)
async def get_seller_profile(seller: SellerDep):
    return seller

# Get all shipments created by the seller
@router.get("/shipments", response_model=list[ShipmentRead])
async def get_shipments(seller: SellerDep):
    return seller.shipments

# @router.get("/dashboard")
# async def get_dashboard(token: Annotated[str, Depends(oauth2_scheme_seller)],
#                         session: SessionDep,)-> Seller:
#     data= decode_access_token(token)

#     if data is None:
#         raise InvalidToken()

#     seller= await session.get(Seller, data["user"]["id"])

#     return seller

@router.get("/logout")
async def logout_seller(token_data: Annotated[dict, Depends(get_seller_access_token)],):
    await add_jti_to_blacklist(token_data["jti"])
    return {
        "detail": "Successfully Logged Out"
    }