from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic.main import BaseModel


class ChatParticipantGet(BaseModel):
    id: int
    chat_id: int
    user_id: int
    role: Enum
    joined_at: datetime


class ChatParticipantPost(BaseModel):
    chat_id: int
    user_id: int
    role: Enum


class ChatParticipantPatch(BaseModel):
    role: Optional[Enum] = None

    class Config:
        from_attributes = True
