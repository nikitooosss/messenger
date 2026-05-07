from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel


class UserGet(BaseModel):
    id: int
    uniq_name: str
    name: Optional[str] = None
    password_hash: str
    is_active: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    last_seen: datetime


class UserPost(BaseModel):
    uniq_name: str
    name: Optional[str] = None
    password_hash: str


class UserPatch(BaseModel):
    uniq_name: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True
