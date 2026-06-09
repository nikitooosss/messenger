from ..manager import WSManager


class UserTypingRecipients:
    def resolve(self, event, ws_manager: WSManager) -> set[int]:
        return ws_manager.rooms.get(event.chat_id, set())


class UserPresenceRecipients:
    def resolve(self, event, ws_manager: WSManager) -> set[int]:
        recipients = set()

        for chat_id in ws_manager.user_to_chats[event.user.id]:
            recipients.update(ws_manager.rooms.get(chat_id, set()))

        recipients.discard(event.user.id)

        return recipients
