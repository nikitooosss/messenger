from fastapi import WebSocket

from backend.services.chat import ChatService

from .schemas.events import BaseEvent


class WSManager:
    def __init__(self):
        self.active: dict[int, set[WebSocket]] = {}
        self.rooms: dict[int, set[int]] = {}
        self.user_to_chats: dict[int, set[int]] = {}

        self.routes = {}

    def get_chat_users(self, chat_id: int) -> set[int]:
        return self.rooms.get(chat_id, set())

    def get_user_chats(self, user_id: int) -> set[int]:
        return self.user_to_chats.get(user_id, set())

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
        chat_service: ChatService,
    ):
        await websocket.accept()

        if user_id not in self.active:
            self.active[user_id] = set()

        self.active[user_id].add(websocket)

        chats = await chat_service.get_chats_by_user_id(user_id=user_id)
        chat_ids = {chat.id for chat in chats}

        self.user_to_chats[user_id] = chat_ids

        for chat_id in chat_ids:
            self.rooms.setdefault(chat_id, set()).add(user_id)

    async def disconnect(self, user_id: int, websocket: WebSocket):
        self.active[user_id].discard(websocket)

        if not self.active[user_id]:
            self.active.pop(user_id, None)

            chat_ids = self.user_to_chats.get(user_id, set())

            for chat_id in chat_ids:
                room = self.rooms.get(chat_id)

                if room:
                    room.discard(user_id)

                    if not room:
                        self.rooms.pop(chat_id, None)

        return self.active.get(user_id, None)

    def add_user_to_room(self, chat_id: int, user_id: int):
        if user_id not in self.active:
            return

        self.rooms.setdefault(chat_id, set()).add(user_id)
        self.user_to_chats.setdefault(user_id, set()).add(chat_id)

    def remove_user_from_room(self, chat_id: int, user_id: int):
        room = self.rooms.get(chat_id)

        if room:
            room.discard(user_id)

            if not room:
                self.rooms.pop(chat_id, None)

        user_chats = self.user_to_chats.get(user_id)
        if user_chats:
            user_chats.discard(chat_id)

            if not user_chats:
                self.user_to_chats.pop(user_id, None)

    async def broadcast(
        self,
        event: BaseEvent,
        recipients: set[int],
    ):
        data = event.model_dump(mode="json")

        for user_id in recipients:
            websockets = self.active.get(user_id, set())

            for websocket in websockets:
                await websocket.send_json(data)

    async def broadcast_error(self, user_id: int, message: str):
        websockets = self.active.get(user_id)

        if not websockets:
            return

        for websocket in websockets:
            await websocket.send_json({"type": "error", "message": message})
