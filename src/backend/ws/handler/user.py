from ..schemas.events import (
    TypeEvent,
    UserStartTypingEvent,
    UserStopTypingEvent,
)


class UserStartTypingHandler:
    def handle(self, event: UserStartTypingEvent):
        user_id = event.user_id
        chat_id = event.chat_id

        return UserStartTypingEvent(
            type=TypeEvent.user_start_typing, user_id=user_id, chat_id=chat_id
        )


class UserStopTypingHandler:
    def handle(self, event: UserStopTypingEvent):
        user_id = event.user_id
        chat_id = event.chat_id

        return UserStopTypingEvent(
            type=TypeEvent.user_stop_typing, user_id=user_id, chat_id=chat_id
        )
