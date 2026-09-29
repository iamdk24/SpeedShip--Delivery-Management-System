from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel, Session
from .models import Shipment
from typing import Annotated
from fastapi import Depends
from app.config import db_settings
import asyncio
from sqlalchemy.orm import sessionmaker


engine=create_async_engine(
    url=db_settings.POSTGRES_URL,
    echo=True,
)


async def create_db_tables():
    async with engine.begin() as connection:
        from app.database.models import Shipment
        await connection.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async_session=sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


 
 
 

