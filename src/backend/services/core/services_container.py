from dataclasses import dataclass

from ..chat import ChatService
from ..chat_participant import ChatParticipantService
from ..message import MessageService
from ..user import UserService


@dataclass
class ServicesContainer:
    chat_service: ChatService
    message_service: MessageService
    chat_participant_service: ChatParticipantService
    user_service: UserService
