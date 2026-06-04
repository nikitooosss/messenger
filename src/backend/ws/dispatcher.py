from backend.services.core.services_container import ServicesContainer
from backend.ws.handler.chat import (
    ChatCreateHandler,
    ChatDeleteHandler,
    ChatUpdateHandler,
)
from backend.ws.handler.chat_participant import (
    ChatParticipantCreateHandler,
    ChatParticipantDeleteHandler,
    ChatParticipantUpdateHandler,
)
from backend.ws.handler.message import (
    MessageCreateHandler,
    MessageDeleteHandler,
    MessageUpdateHandler,
)
from backend.ws.handler.user import (
    UserStartTypingHandler,
    UserStopTypingHandler,
)
from backend.ws.schemas.events import BaseEvent, TypeEvent


class WSDispatcher:
    def __init__(self):
        self.handlers = {
            TypeEvent.chat_create: ChatCreateHandler(),
            TypeEvent.chat_update: ChatUpdateHandler(),
            TypeEvent.chat_delete: ChatDeleteHandler(),
            TypeEvent.chat_participant_create: ChatParticipantCreateHandler(),
            TypeEvent.chat_participant_update: ChatParticipantUpdateHandler(),
            TypeEvent.chat_participant_delete: ChatParticipantDeleteHandler(),
            TypeEvent.message_create: MessageCreateHandler(),
            TypeEvent.message_update: MessageUpdateHandler(),
            TypeEvent.message_delete: MessageDeleteHandler(),
            TypeEvent.user_start_typing: UserStartTypingHandler(),
            TypeEvent.user_stop_typing: UserStopTypingHandler(),
        }

    async def dispatch(self, event: BaseEvent, services: ServicesContainer) -> BaseEvent:
        handler = self.handlers.get(event.type)

        if handler is None:
            raise ValueError(f"Unknown event type: {event.type}")

        return await handler.handle(event, services)
