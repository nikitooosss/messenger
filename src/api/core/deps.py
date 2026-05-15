from fastapi import Depends

from api.database import get_db
from api.services import (
    ChatParticipantService,
    ChatService,
    MessageService,
    UserService,
)


def get_message_service(db=Depends(get_db)):
    return MessageService(db)


def get_user_service(db=Depends(get_db)):
    return UserService(db)


def get_chat_service(db=Depends(get_db)):
    return ChatService(db)


def get_chat_participant_service(db=Depends(get_db)):
    return ChatParticipantService(db)
