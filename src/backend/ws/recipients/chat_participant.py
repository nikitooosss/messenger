from ..manager import WSManager


class ChatParticipantRecipients:
    def resolve(self, event, ws_manager: WSManager) -> set[int]:
        return ws_manager.rooms.get(event.chat_participant.chat_id, set())

