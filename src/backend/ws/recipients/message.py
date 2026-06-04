from ..manager import WSManager


class MessageRecipients:
    def resolve(self, event, ws_manager: WSManager) -> set[int]:
        return ws_manager.rooms.get(event.message.chat_id, set())
