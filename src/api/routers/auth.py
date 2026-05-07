from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.main import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import ACCESS_TOKEN_EXPIRE_MINUTES
from api.core import create_access_token, hash_password, verify_password
from api.database import User, get_db
from api.schemas import UserGet, UserRegister

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


class Token(BaseModel):
    access_token: str
    token_type: str


async def authenticate_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    uniq_name: str,
    password: str,
) -> UserGet | None:
    stmt = select(User).where(User.uniq_name == uniq_name)
    result = await db.execute(stmt)
    user_orm = result.scalar_one_or_none()

    if user_orm is None:
        return None

    if not verify_password(password, user_orm.password_hash):
        return None

    return UserGet.model_validate(user_orm, from_attributes=True)


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


@router_auth.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.uniq_name}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
