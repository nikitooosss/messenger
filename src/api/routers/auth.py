from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core import hash_password
from api.database import User, get_db
from api.schemas.auth import UserRegister

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router_auth.post("/register")
async def register_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_data: UserRegister,
):
    stmt = select(User).where(User.uniq_name == user_data.uniq_name)
    result = await db.execute(stmt)
    user_orm = result.scalar_one_or_none()

    if user_orm is not None:
        raise HTTPException(
            status_code=409, detail="A user with that name already exists"
        )

    user = User(**user_data.model_dump(exclude_unset=True))

    hashed_password = hash_password(user.password_hash)
    user.password_hash = hashed_password

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user
