from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.api.schemas.delivery_partner import DeliveryPartnerCreate, DeliveryPartnerRead, DeliveryPartnerUpdate
from app.api.dependencies import DeliveryPartnerDep, DeliveryPartnerServiceDep, SellerServiceDep, SessionDep, get_partner_access_token


from app.api.schemas.shipment import ShipmentRead
from app.api.tag import ApiTag
from app.core.exceptions import EntityNotFound
from app.database.redis import add_jti_to_blacklist
from app.utils import TEMPLATE_DIR, decode_access_token
from app.config import app_settings

router=APIRouter(prefix="/partner", tags=[ApiTag.PARTNER])


# Register a delivery partner
@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_delivery_partner(seller: DeliveryPartnerCreate, service: DeliveryPartnerServiceDep):
    return await service.add(seller)

#Verify Partner Email
@router.get("/verify")
async def verify_delivery_partner_email(token:str, service: DeliveryPartnerServiceDep):
    await service.verify_email(token)
    return{"detail":"Account Verified"}

#Email Password reset link for Partner
@router.get("/forgot_password")
async def forgot_password(email: EmailStr, service: DeliveryPartnerServiceDep):
    await service.send_password_reset_link(email, router_prefix="partner")
    return{"detail":"Check Email for Password reset link"}

#Password Reset Form
@router.get("/reset_password_form")
async def get_reset_password_form(request:Request,token: str):
    templates=Jinja2Templates(TEMPLATE_DIR)

    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={"reset_url":f"https://{app_settings.APP_DOMAIN}/partner/reset_password?token={token}"}
    )

# Reset Partner Password
@router.post("/reset_password")
async def reset_password(token: str,password: Annotated[str,Form()], service: DeliveryPartnerServiceDep):
    await service.reset_password(token, password)
    return{"detail":"Password reset Successful"}

## Get all shipments assigned to the delivery partner
@router.get("/shipments", response_model=list[ShipmentRead])
async def get_shipments(partner: DeliveryPartnerDep):
    return partner.shipments

# Login the delivery partner
@router.post("/login")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: DeliveryPartnerServiceDep
    ):
    token = await service.token(request_form.username, request_form.password)
    return{
        "access_token": token,
        "type": "JWT"
    }


@router.get("/logout")
async def logout_delivery_partner(token_data: Annotated[dict, Depends(get_partner_access_token)],):
    await add_jti_to_blacklist(token_data["jti"])
    return {
        "detail": "Successfully Logged Out"
    }

# Update the delivery partner

@router.post("/")
async def update_delivery_partner(partner_update: DeliveryPartnerUpdate,
                                  partner: DeliveryPartnerDep, service: DeliveryPartnerServiceDep):
    update=partner_update.model_dump(exclude_none=True)
    if not update:
        raise EntityNotFound()
    
    return await service.update(partner.sqlmodel_update(update))