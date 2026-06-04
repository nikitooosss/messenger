from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from pydantic.main import BaseModel

from ...database.models import UserRole


class ChatParticipantGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    user_id: int
    role: UserRole
    joined_at: datetime


class ChatParticipantPost(BaseModel):
    chat_id: int
    user_id: int
    role: UserRole


class ChatParticipantPatch(BaseModel):
    id: int
    role: Optional[UserRole] = None


class ChatParticipantDelete(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    user_id: int
