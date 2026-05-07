from typing import Optional

from pydantic.main import BaseModel

class UserRegister(BaseModel):
    uniq_name: str
    name: Optional[str] = None
    password_hash: str
