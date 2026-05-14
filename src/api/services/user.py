from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import User, get_db
from api.schemas import UserGet, UserPatch, UserPost
from api.core import hash_password


class UserService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db = db

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
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def delete_user(
        self,
        user_id: int,
    ):
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        await self.db.delete(user)
        await self.db.commit()

        return None
