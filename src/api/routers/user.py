from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import User, get_db
from api.schemas import UserGet, UserPatch, UserPost
from api.core import get_current_user 

router_user = APIRouter(
    prefix="/user",
    tags=["User"],
)

@router_user.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router_user.get("/get", response_model=list[UserGet])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return users


@router_user.get("/get/{user_id}", response_model=UserGet)
async def get_user_by_id(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user_orm = result.scalar_one_or_none()

    if user_orm is None:
        raise HTTPException(status_code=404, detail="User not found")

    user = UserGet.model_validate(user_orm, from_attributes=True)

    return user


@router_user.post("/create", response_model=UserPost)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_data: UserPost,
):
    stmt = select(User).where(User.uniq_name == user_data.uniq_name)
    result = await db.execute(stmt)
    user_orm = result.scalar_one_or_none()

    if user_orm is not None:
        raise HTTPException(
            status_code=409, detail="A user with that name already exists"
        )

    user = User(**user_data.model_dump(exclude_unset=True))

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router_user.patch("/{user_id}", response_model=UserPatch)
async def update_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    user_data: UserPatch,
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


@router_user.delete("/{user_id}", status_code=204)
async def delete_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
