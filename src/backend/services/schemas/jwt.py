from typing import Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    id: int
    uniq_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
