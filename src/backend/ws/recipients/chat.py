from ..manager import WSManager
from ..schemas.events import TypeEvent


class ChatRecipients:
    def resolve(self, event, ws_manager: WSManager) -> set[int]:
        if (
            getattr(event, "type", None) == TypeEvent.chat_deleted
            and getattr(event, "participants", None) is not None
        ):
            return {p.user_id for p in event.participants}
        return ws_manager.rooms.get(event.chat.id, set())
