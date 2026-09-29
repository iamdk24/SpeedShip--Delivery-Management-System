from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from contextlib import asynccontextmanager

from fastapi.routing import APIRoute

from app.api.tag import ApiTag
from app.core.exceptions import add_exception_handlers
from .api.schemas.shipment import ShipmentRead, ShipmentCreate, ShipmentUpdate
from datetime import datetime, timedelta


from app.database.session import create_db_tables
from sqlmodel import Session
from .database.models import Shipment, ShipmentStatus

from app.api.router import master_router

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield

description="""
    Delivery Management System
    ### Seller
    - Submit Shipment Effortlessly
    - Share tracking links with customers

    ### Delivery Agent
    - Auto Accept Shipments
    - Track and Update Shipment Status
    - Email Notifications
    """

def custom_generate_unique_id_function(route: APIRoute)->str:
    return route.name
app=FastAPI(lifespan= lifespan_handler, title="SpeedShip Api", description=description, version="0.1.0",
            openapi_tags=[
                {
                    "name": ApiTag.SHIPMENT,
                    "description": "Operations related to Shipments"
                },
                {
                    "name": ApiTag.SELLER,
                    "description": "Operations related to Seller"
                },
                {
                    "name": ApiTag.PARTNER,
                    "description": "Operations related to Delivery Partner"
                }

            ],
            generate_unique_id_function=custom_generate_unique_id_function)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(master_router)

add_exception_handlers(app)

