from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.schemas.jwt import TokenData

from ..database.get_db import get_db
from ..database.models import User
from .core.jwt import get_jwt_payload
from .core.password import hash_password
from .schemas.user import UserGet, UserPatch, UserPost


class UserService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db = db

    async def get_current_user(
        self,
        token: str,
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = get_jwt_payload(token=token)
            if payload is None:
                raise credentials_exception

            token_data = TokenData.model_validate(payload)

        except InvalidTokenError:
            raise credentials_exception

        stmt = select(User).where(User.uniq_name == token_data.uniq_name)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        return user

    async def get_all_users(
        self,
    ):
        stmt = select(User)
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        return users

    async def get_user_by_id(
        self,
        user_id: int,
    ):
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user_orm = result.scalar_one_or_none()

        if user_orm is None:
            raise HTTPException(status_code=404, detail="User not found")

        user = UserGet.model_validate(user_orm, from_attributes=True)

        return user

    async def _get_user_orm_by_id(self, user_id: int) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    async def create_user(
        self,
        user_data: UserPost,
    ):
        stmt = select(User).where(User.uniq_name == user_data.uniq_name)
        result = await self.db.execute(stmt)
        user_orm = result.scalar_one_or_none()

        if user_orm is not None:
            raise HTTPException(
                status_code=409, detail="A user with that name already exists"
            )

        user = User(**user_data.model_dump(exclude_unset=True))

        hashed_password = hash_password(user.password_hash)
        user.password_hash = hashed_password

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_user(
        self,
        user_id: int,
        user_data: UserPatch,
    ):
        user = await self._get_user_orm_by_id(user_id)

        update_data = user_data.model_dump(exclude_unset=True, exclude={"id"})

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_last_seen(
        self,
        user_id: int,
    ):
        user = await self._get_user_orm_by_id(user_id)

        user.last_seen = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_is_active_on_opposite(
        self,
        user_id: int,
    ):
        user = await self._get_user_orm_by_id(user_id=user_id)
        current_active_status = user.is_active

        if current_active_status:
            user.is_active = False
        user.is_active = True

        await self.db.commit()
        await self.db.refresh(user)

    async def delete_user(
        self,
        user_id: int,
    ):
        user = await self._get_user_orm_by_id(user_id)

        await self.db.delete(user)
        await self.db.commit()

        return None
