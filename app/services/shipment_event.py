from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.services.base import BaseService
from app.services.notification import NotificationService
from app.config import app_settings
from app.utils import generate_url_safe_token
from app.worker.tasks import send_email_with_template

class ShipmentEventService(BaseService):
    def __init__(self,session):
        super().__init__(ShipmentEvent, session)


    async def add(self, shipment: Shipment, location:int=None, status: ShipmentStatus=None, description: str = None)->ShipmentEvent:
        if location is None  or status is None:
            last_event=await self.get_latest_event(shipment)
            if last_event is None:
                raise ValueError(
                    "Location and status are required when creating shipments"
                )
            if location is None:
                location=last_event.location
            if status is None:
                status=last_event.status
        new_event=ShipmentEvent(
            location=location,
            status=status,
            description=description if description else self._generate_description(status,location),
            shipment_id=shipment.id
        )

        await self._notify(shipment,status)
        return await self._add(new_event)

    async def get_latest_event(self, shipment: Shipment):
        timeline=shipment.timeline

        if not timeline:
            return None
        timeline.sort(key=lambda event: event.created_at)
        return timeline[-1]

    def _generate_description(self, status: ShipmentStatus, location: int):
        match status:
            case ShipmentStatus.placed:
                return "assigned delivery partner"
            case ShipmentStatus.delivered:
                return "Successfully delivered"
            case ShipmentStatus.out_for_delivery:
                return "Shipment out for delivery"
            case ShipmentStatus.cancelled:
                return "Cancelled by the seller"
            case _:
                return f"scanned at {location}"

    async def _notify(self, shipment: Shipment, status: ShipmentStatus):

        if status==ShipmentStatus.in_transit:
            return

        subject: str
        context={}
        template_name:str
        match status:
            case ShipmentStatus.placed:
                subject="Your Order is Placed"
                context["seller"]=shipment.seller.name
                context["partner"]=shipment.delivery_partner.name
                context["id"]=shipment.id
                template_name="mail_placed.html"

                # await self.notification_service.send_email(recipients=[shipment.client_contact_email],
                #                                      subject="Your Order is Shipped",
                #                                      body=f"Your order with {shipment.seller.name} is picked up by {shipment.delivery_partner.name} and is on its way to you.")
            case ShipmentStatus.out_for_delivery:
                subject="Your Order is Out for Delivery"
                template_name="mail_out_for_delivery.html"
            case ShipmentStatus.delivered:
                subject="Your Order is Delivered"
                token=generate_url_safe_token({"id":str(shipment.id)})
                context["review_url"]=f"https://{app_settings.APP_DOMAIN}/shipment/review?token={token}"
                template_name="mail_delivered.html"
            case ShipmentStatus.cancelled:
                subject="Your Order is Cancelled"
                template_name="mail_cancelled.html"


        send_email_with_template.delay(recipients=[shipment.client_contact_email],
                                                                    subject=subject,
                                                                    context=context,
                                                                    template_name=template_name)
                
            
                