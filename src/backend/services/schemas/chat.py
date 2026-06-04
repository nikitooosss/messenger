from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from pydantic.main import BaseModel

from .chat_participant import ChatParticipantGet


class ChatDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_group: bool
    created_at: datetime

    participants: list[ChatParticipantGet]


class ChatGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_group: bool
    created_at: datetime


class ChatPost(BaseModel):
    name: str
    is_group: bool


class ChatPatch(BaseModel):
    id: int
    name: Optional[str] = None


class ChatDelete(BaseModel):
    id: int

    class Config:
        from_attributes = True
