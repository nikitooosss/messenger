from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel


class MessageGet(BaseModel):
    id: int
    chat_id: int
    user_id: int
    content: str
    created_at: datetime


class MessagePost(BaseModel):
    chat_id: int
    user_id: int
    content: str


class MessagePatch(BaseModel):
    content: Optional[str] = None

    class Config:
        from_attributes = True
