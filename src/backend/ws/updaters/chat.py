from ..manager import WSManager


class ChatCreateStateUpdater:
    def update(self, event, ws_manager: WSManager):
        ws_manager.rooms.setdefault(event.chat.id, set())

        for p in event.participants:
            ws_manager.add_user_to_room(chat_id=event.chat.id, user_id=p.user_id)


class ChatDeleteStateUpdater:
    def update(self, event, ws_manager: WSManager):
        ws_manager.rooms.pop(event.chat.id, None)

        for p in event.participants:
            user_chats = ws_manager.get_user_chats(user_id=p.user_id)

            if user_chats:
                user_chats.discard(event.chat.id)

                if not user_chats:
                    ws_manager.user_to_chats.pop(
                        p.user_id,
                        None,
                    )
