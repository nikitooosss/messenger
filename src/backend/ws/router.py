from .manager import WSManager
from .recipients.chat import ChatRecipients
from .recipients.chat_participant import ChatParticipantRecipients
from .recipients.message import MessageRecipients
from .recipients.user import UserPresenceRecipients, UserTypingRecipients
from .schemas.events import BaseEvent, TypeEvent


class EventRouter:
    def __init__(self):
        self.routes = {
            TypeEvent.message_created: MessageRecipients(),
            TypeEvent.message_updated: MessageRecipients(),
            TypeEvent.message_deleted: MessageRecipients(),
            TypeEvent.chat_created: ChatRecipients(),
            TypeEvent.chat_updated: ChatRecipients(),
            TypeEvent.chat_deleted: ChatRecipients(),
            TypeEvent.chat_participant_created: ChatParticipantRecipients(),
            TypeEvent.chat_participant_updated: ChatParticipantRecipients(),
            TypeEvent.chat_participant_deleted: ChatParticipantRecipients(),
            TypeEvent.user_start_typing: UserTypingRecipients(),
            TypeEvent.user_stop_typing: UserTypingRecipients(),
            TypeEvent.user_online: UserPresenceRecipients(),
            TypeEvent.user_offline: UserPresenceRecipients(),
        }

    def route(self, event: BaseEvent, ws_manager: WSManager):
        route = self.routes.get(event.type)

        if route is None:
            raise ValueError(f"Unknown event type: {event.type}")

        return route.resolve(event, ws_manager)
