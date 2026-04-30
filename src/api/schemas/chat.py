from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel


class ChatGet(BaseModel):
    id: int
    name: str
    is_group: bool
    created_at: datetime


class ChatPost(BaseModel):
    name: str
    is_group: bool


class ChatPatch(BaseModel):
    name: Optional[str] = None

    class Config:
        from_attributes = True
