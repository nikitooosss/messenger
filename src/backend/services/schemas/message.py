from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, model_validator
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
    created_at: Optional[datetime] = None

    @model_validator(mode="after")
    def _default_created_at(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        return self


class MessagePatch(BaseModel):
    id: int
    content: Optional[str] = None


class MessageDelete(BaseModel):
    id: int
    chat_id: int

    class Config:
        from_attributes = True
