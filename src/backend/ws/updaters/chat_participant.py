from ..manager import WSManager


class ChatParticipantCreateStateUpdater:
    def update(self, event, ws_manager: WSManager):
        user_id = event.chat_participant.user_id
        chat_id = event.chat_participant.chat_id

        if ws_manager.active.get(user_id):
            ws_manager.rooms.setdefault(
                chat_id,
                set(),
            ).add(user_id)

            ws_manager.user_to_chats.setdefault(
                user_id,
                set(),
            ).add(chat_id)


class ChatParticipantDeleteStateUpdater:
    def update(self, event, ws_manager: WSManager):
        chat_id = event.chat_participant.chat_id
        user_id = event.chat_participant.user_id

        room = ws_manager.rooms.get(chat_id)

        if room:
            room.discard(user_id)

        user_chats = ws_manager.user_to_chats.get(user_id)

        if user_chats:
            user_chats.discard(chat_id)

            if not user_chats:
                ws_manager.user_to_chats.pop(user_id, None)
