from ..manager import WSManager
from ..schemas.events import TypeEvent


class ChatRecipients:
    def resolve(self, event, ws_manager: WSManager) -> set[int]:
        event_type = getattr(event, "type", None)

        if (
            event_type == TypeEvent.chat_deleted
            and getattr(event, "participants", None) is not None
        ):
            return {p.user_id for p in event.participants}

        if (
            event_type == TypeEvent.chat_created
            and getattr(event, "participants", None) is not None
        ):
            return {
                p.user_id
                for p in event.participants
                if p.user_id in ws_manager.active
            }

        return ws_manager.rooms.get(event.chat.id, set())
