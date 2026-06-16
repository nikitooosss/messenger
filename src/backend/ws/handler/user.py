from backend.services.core.services_container import ServicesContainer

from ..schemas.events import (
    TypeEvent,
    UserStartTypingEvent,
    UserStopTypingEvent,
)


class UserStartTypingHandler:
    async def handle(
        self,
        event: UserStartTypingEvent,
        services: ServicesContainer,
        user_id: int,
    ) -> UserStartTypingEvent:
        return UserStartTypingEvent(
            type=TypeEvent.user_start_typing,
            user_id=event.user_id,
            chat_id=event.chat_id,
        )


class UserStopTypingHandler:
    async def handle(
        self,
        event: UserStopTypingEvent,
        services: ServicesContainer,
        user_id: int,
    ) -> UserStopTypingEvent:
        return UserStopTypingEvent(
            type=TypeEvent.user_stop_typing,
            user_id=event.user_id,
            chat_id=event.chat_id,
        )
