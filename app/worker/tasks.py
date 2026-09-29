from celery import Celery
from asgiref.sync import async_to_sync
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.config import db_settings, notification_settings
from app.utils import TEMPLATE_DIR

app=Celery("api_tasks", broker=db_settings.REDIS_URL(db=9),)

fast_mail=FastMail(ConnectionConfig(
            **notification_settings.model_dump(),
            TEMPLATE_FOLDER=TEMPLATE_DIR
        ))

send_message=async_to_sync(fast_mail.send_message)

@app.task
def send_mail(recipients: list[EmailStr], subject: str, body: str):
    send_message(MessageSchema(recipients=recipients,
                               subject=subject,
                               body=body,
                               subtype=MessageType.plain))
    return "Message Sent"


@app.task
def send_email_with_template(recipients: list[EmailStr], subject:str, context: dict, template_name: str):
    send_message(MessageSchema(recipients=recipients,
                               subject=subject,
                               template_body=context,
                               subtype=MessageType.html),
                               template_name=template_name)