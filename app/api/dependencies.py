from typing import Annotated

from fastapi import BackgroundTasks, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.exceptions import ClientNotAuthorized, InvalidToken
from app.database.models import DeliveryPartner, Seller
from app.database.redis import is_jti_blacklisted
from app.database.session import get_session
from app.services.delivery_partner import DeliveryPartnerService
from app.services.shipment import ShipmentService
from app.services.seller import SellerService
from app.core.security import oauth2_scheme_seller, oauth2_scheme_partner
from app.services.shipment_event import ShipmentEventService
from app.utils import decode_access_token


SessionDep=Annotated[AsyncSession, Depends(get_session)]

#Shipment Service dep
def get_shipment_service(session: SessionDep, ):
    return ShipmentService(session, DeliveryPartnerService(session), ShipmentEventService(session,))
# Shipment Service dep annotation
ShipmentServiceDep=Annotated[ShipmentService, Depends(get_shipment_service)]

#Seller Service dep
def get_seller_service(session: SessionDep,):
    return SellerService(session,)
# Shipment Service dep annotation
SellerServiceDep=Annotated[SellerService, Depends(get_seller_service)]

#Delivery Partner Service dep
def get_delivery_partner_service(session:SessionDep, ):
    return DeliveryPartnerService(session, )
#Delivery Partner Service dep annotation
DeliveryPartnerServiceDep=Annotated[DeliveryPartnerService, Depends(get_delivery_partner_service)]

#Access token data dep
async def _get_access_token(token: str)->dict:
    data= decode_access_token(token)
    
    if data is None or await is_jti_blacklisted(data["jti"]):
        raise InvalidToken()
    return data

#Seller Access token data
async def get_seller_access_token(token: Annotated[str, Depends(oauth2_scheme_seller)]):
    return await _get_access_token(token)

#Delivery Partner Access token data
async def get_partner_access_token(token: Annotated[str, Depends(oauth2_scheme_partner)]):
    return await _get_access_token(token)

#Logged In Seller
async def get_logged_in_seller(token_data: Annotated[dict, Depends(get_seller_access_token)],
                       session: SessionDep):
    seller= await session.get(Seller, UUID(token_data["user"]["id"]))

    if seller is None:
        raise ClientNotAuthorized()
    return seller

#Logged In Partner
async def get_logged_in_partner(token_data: Annotated[dict, Depends(get_partner_access_token)],
                       session: SessionDep):
    partner= await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))

    if partner is None:
            raise ClientNotAuthorized()
    return partner

#Seller dep
SellerDep=Annotated[Seller, Depends(get_logged_in_seller)]

#Delivery Partner dep
DeliveryPartnerDep=Annotated[DeliveryPartner, Depends(get_logged_in_partner)]