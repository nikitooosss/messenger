from fastapi import Depends

from ...database.get_db import get_db
from ...services.auth import AuthService
from ...services.chat import ChatService
from ...services.chat_participant import ChatParticipantService
from ...services.jwt import JWTService
from ...services.message import MessageService
from ...services.user import UserService


def get_message_service(db=Depends(get_db)):
    return MessageService(db)


def get_user_service(db=Depends(get_db)):
    return UserService(db)


def get_chat_service(db=Depends(get_db)):
    return ChatService(db)


def get_chat_participant_service(db=Depends(get_db)):
    return ChatParticipantService(db)


def get_auth_service(db=Depends(get_db)):
    return AuthService(db)


def get_jwt_service(db=Depends(get_db)):
    return JWTService(db)
