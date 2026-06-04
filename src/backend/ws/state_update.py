from .manager import WSManager
from .schemas.events import TypeEvent
from .updaters.chat import ChatCreateStateUpdater, ChatDeleteStateUpdater
from .updaters.chat_participant import (
    ChatParticipantCreateStateUpdater,
    ChatParticipantDeleteStateUpdater,
)


class StateUpdater:
    def __init__(self):
        self.updaters = {
            TypeEvent.chat_created: ChatCreateStateUpdater(),
            TypeEvent.chat_deleted: ChatDeleteStateUpdater(),
            TypeEvent.chat_participant_created: ChatParticipantCreateStateUpdater(),
            TypeEvent.chat_participant_deleted: ChatParticipantDeleteStateUpdater(),
        }

    def update(self, event, ws_manager: WSManager):
        updater = self.updaters.get(event.type)

        if updater:
            updater.update(
                event=event,
                ws_manager=ws_manager,
            )
