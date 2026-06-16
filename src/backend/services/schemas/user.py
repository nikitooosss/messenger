from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, field_serializer
from pydantic.main import BaseModel


def _serialize_naive_as_utc(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=__import__("datetime").timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


class UserGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uniq_name: str
    name: Optional[str] = None
    is_active: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    last_seen: datetime

    @field_serializer("created_at", "last_seen")
    def _ser_dt(self, v: datetime) -> str:
        return _serialize_naive_as_utc(v)


class UserPublic(BaseModel):
    """Схема для отправки данных пользователя клиенту (без пароля)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    uniq_name: str
    name: Optional[str] = None
    is_active: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    last_seen: datetime

    @field_serializer("created_at", "last_seen")
    def _ser_dt(self, v: datetime) -> str:
        return _serialize_naive_as_utc(v)


class UserPost(BaseModel):
    uniq_name: str
    name: Optional[str] = None
    password_hash: str


class UserPatch(BaseModel):
    uniq_name: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True
