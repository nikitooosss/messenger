from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic.main import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import ALGORITHM, SECRET_KEY
from api.database import User, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class TokenData(BaseModel):
    uniq_name: Optional[str] = None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uniq_name = payload.get("sub")
        if uniq_name is None:
            raise credentials_exception
        token_data = TokenData(uniq_name=uniq_name)
    except InvalidTokenError:
        raise credentials_exception

    stmt = select(User).where(User.uniq_name == token_data.uniq_name)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user
