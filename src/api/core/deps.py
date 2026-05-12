from fastapi import Depends

from api.services import MessageService
from api.database import get_db

def get_message_service(db = Depends(get_db)):
    return MessageService(db)
