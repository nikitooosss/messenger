from ..manager import WSManager


class ChatRecipients:
    def resolve(self, event, ws_manager: WSManager) -> set[int]:
        return ws_manager.rooms.get(event.chat.id, set())
