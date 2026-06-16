from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.schemas.auth import UserRegister
from ..database.get_db import get_db
from ..database.models import User
from .core.password import hash_password, verify_password
from .schemas.user import UserGet, UserPublic


class AuthService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db = db

    async def authenticate_user(
        self,
        uniq_name: str,
        password: str,
    ) -> UserGet | None:
        stmt = select(User).where(User.uniq_name == uniq_name)
        result = await self.db.execute(stmt)
        user_orm = result.scalar_one_or_none()

        if user_orm is None:
            return None

        if not verify_password(password, user_orm.password_hash):
            return None

        return UserGet.model_validate(user_orm, from_attributes=True)

    async def register_user(self, user_data: UserRegister):
        stmt = select(User).where(User.uniq_name == user_data.uniq_name)
        result = await self.db.execute(stmt)
        user_orm = result.scalar_one_or_none()

        if user_orm:
            return None

        user = User(**user_data.model_dump(exclude_unset=True))

        hashed_password = hash_password(user.password_hash)
        user.password_hash = hashed_password

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user
