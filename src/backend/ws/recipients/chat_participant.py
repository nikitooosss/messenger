from ..manager import WSManager
from ..schemas.events import TypeEvent


class ChatParticipantRecipients:
    def resolve(self, event, ws_manager: WSManager) -> set[int]:
        recipients = set(ws_manager.rooms.get(event.chat_participant.chat_id, set()))
        if event.type == TypeEvent.chat_participant_created:
            joiner = event.chat_participant.user_id
            if joiner in ws_manager.active:
                recipients.add(joiner)
        return recipients

