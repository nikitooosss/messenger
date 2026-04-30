from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel


class UserGet(BaseModel):
    id: int
    uniq_name: str
    name: str
    is_active: bool
    avatar_url: str | None = None
    created_at: datetime
    last_seen: datetime


class UserPost(BaseModel):
    uniq_name: str
    name: str
    password_hash: str


class UserPatch(BaseModel):
    uniq_name: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True
