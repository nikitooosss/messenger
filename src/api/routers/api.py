from fastapi import APIRouter

from .auth import router_auth
from .chat import router_chat
from .chat_participant import router_chat_participant
from .message import router_message
from .user import router_user

api_router = APIRouter()
api_router.include_router(router_user)
api_router.include_router(router_chat)
api_router.include_router(router_message)
api_router.include_router(router_chat_participant)
api_router.include_router(router_auth)
