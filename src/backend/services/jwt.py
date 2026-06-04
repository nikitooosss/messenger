from datetime import timedelta
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..database.get_db import get_db
from .core.jwt import create_access_token
from .schemas.jwt import Token, TokenData


class JWTService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db = db

    async def get_access_token(self, data: TokenData) -> Token:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=data.model_dump(),
            expires_delta=access_token_expires,
        )

        return Token(access_token=access_token, token_type="bearer")
