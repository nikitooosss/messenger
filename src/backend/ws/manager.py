import asyncio

from fastapi import WebSocket, WebSocketDisconnect

from backend.services.chat import ChatService

from .schemas.events import BaseEvent


class WSManager:
    def __init__(self):
        self.active: dict[int, set[WebSocket]] = {}
        self.rooms: dict[int, set[int]] = {}
        self.user_to_chats: dict[int, set[int]] = {}

        self._lock = asyncio.Lock()

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        async with self._lock:
            conns = self.active.setdefault(user_id, set())
            first_conn = len(conns) == 0
            conns.add(websocket)

        return first_conn

    async def disconnect(self, user_id: int, websocket: WebSocket):
        async with self._lock:
            conns = self.active.get(user_id)
            if conns is None:
                return None
            conns.discard(websocket)
            if not conns:
                self.active.pop(user_id, None)

            return self.active.get(user_id, None)

    async def add_user_to_room(self, chat_id: int, user_id: int):
        async with self._lock:
            if user_id not in self.active:
                return

            self.rooms.setdefault(chat_id, set()).add(user_id)
            self.user_to_chats.setdefault(user_id, set()).add(chat_id)

    async def remove_user_from_room(self, chat_id: int, user_id: int):
        async with self._lock:
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
        stale: list[tuple[int, WebSocket]] = []

        for user_id in recipients:
            websockets = self.active.get(user_id, set())

            for websocket in websockets:
                try:
                    await websocket.send_json(data)
                except (RuntimeError, WebSocketDisconnect):
                    stale.append((user_id, websocket))

        for user_id, ws in stale:
            self.active.get(user_id, set()).discard(ws)

    async def broadcast_error(self, user_id: int, message: str):
        websockets = self.active.get(user_id)

        if not websockets:
            return

        stale: list[WebSocket] = []
        for websocket in websockets:
            try:
                await websocket.send_json({"type": "error", "message": message})
            except (RuntimeError, WebSocketDisconnect):
                stale.append(websocket)

        for ws in stale:
            websockets.discard(ws)

    def get_chat_users(self, chat_id: int) -> set[int]:
        return self.rooms.get(chat_id, set())

    def get_user_chats(self, user_id: int) -> set[int]:
        return self.user_to_chats.get(user_id, set())

    async def init_online_user(self, user_id: int, chat_service: ChatService):
        chats = await chat_service.get_chats_by_user_id(user_id=user_id)
        chat_ids = [chat.id for chat in chats]

        async with self._lock:
            self.user_to_chats[user_id] = set(chat_ids)

            for chat_id in chat_ids:
                self.rooms.setdefault(chat_id, set()).add(user_id)
