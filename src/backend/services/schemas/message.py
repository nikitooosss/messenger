from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from pydantic.main import BaseModel


class MessageGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    id: int
    content: Optional[str] = None


class MessageDelete(BaseModel):
    id: int

    class Config:
        from_attributes = True
