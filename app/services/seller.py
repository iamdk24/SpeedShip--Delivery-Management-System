from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlmodel import select
import jwt

from app.api.schemas.seller import SellerCreate
from app.database.models import Seller
from app.config import security_settings
from app.services.user import UserService
from app.utils import generate_access_token, decode_access_token


class SellerService(UserService):
    def __init__(self, session: AsyncSession):
          super().__init__(Seller, session,)

    async def add(self, seller_create: SellerCreate) -> Seller:
          return await self._add_user(seller_create.model_dump(),"seller")

    async def token(self, email, password) -> str:
         return await self._generate_token(email,password)