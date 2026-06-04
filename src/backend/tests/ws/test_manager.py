import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.ws.manager import WSManager
from backend.ws.schemas.events import BaseEvent, TypeEvent


@pytest.mark.asyncio
async def test_connect_adds_user_to_active(ws_manager: WSManager):
    user_id = 1
    mock_ws = MagicMock()
    mock_ws.accept = AsyncMock()
    chat_service = MagicMock()
    chat_service.get_chats_by_user_id = AsyncMock(return_value=[])

    await ws_manager.connect(
        user_id=user_id,
        websocket=mock_ws,
        chat_service=chat_service,
    )

    assert user_id in ws_manager.active
    assert ws_manager.active[user_id] == mock_ws
    mock_ws.accept.assert_called_once()


@pytest.mark.asyncio
async def test_connect_loads_user_chats(ws_manager: WSManager):
    user_id = 1
    mock_ws = MagicMock()
    mock_ws.accept = AsyncMock()

    chat1 = MagicMock()
    chat1.id = 10
    chat2 = MagicMock()
    chat2.id = 20

    chat_service = MagicMock()
    chat_service.get_chats_by_user_id = AsyncMock(return_value=[chat1, chat2])

    await ws_manager.connect(
        user_id=user_id,
        websocket=mock_ws,
        chat_service=chat_service,
    )

    assert ws_manager.user_to_chats[user_id] == {10, 20}
    assert ws_manager.rooms[10] == {user_id}
    assert ws_manager.rooms[20] == {user_id}


@pytest.mark.asyncio
async def test_disconnect_removes_user(ws_manager: WSManager):
    user_id = 1
    ws_manager.active[user_id] = MagicMock()
    ws_manager.user_to_chats[user_id] = {10}
    ws_manager.rooms[10] = {user_id}

    await ws_manager.disconnect(user_id=user_id)

    assert user_id not in ws_manager.active
    assert user_id not in ws_manager.user_to_chats
    assert 10 not in ws_manager.rooms


@pytest.mark.asyncio
async def test_disconnect_cleans_empty_rooms(ws_manager: WSManager):
    ws_manager.active[1] = MagicMock()
    ws_manager.user_to_chats[1] = {10}
    ws_manager.rooms[10] = {1}

    await ws_manager.disconnect(user_id=1)

    assert 10 not in ws_manager.rooms


@pytest.mark.asyncio
async def test_add_user_to_room(ws_manager: WSManager):
    ws_manager.active[1] = MagicMock()

    ws_manager.add_user_to_room(chat_id=10, user_id=1)

    assert ws_manager.rooms[10] == {1}
    assert ws_manager.user_to_chats[1] == {10}


@pytest.mark.asyncio
async def test_add_user_to_room_not_active_is_noop(ws_manager: WSManager):
    ws_manager.add_user_to_room(chat_id=10, user_id=999)

    assert 10 not in ws_manager.rooms
    assert 999 not in ws_manager.user_to_chats


@pytest.mark.asyncio
async def test_remove_user_from_room(ws_manager: WSManager):
    ws_manager.active[1] = MagicMock()
    ws_manager.rooms[10] = {1, 2}
    ws_manager.user_to_chats[1] = {10, 20}

    ws_manager.remove_user_from_room(chat_id=10, user_id=1)

    assert ws_manager.rooms[10] == {2}
    assert ws_manager.user_to_chats[1] == {20}


@pytest.mark.asyncio
async def test_remove_user_from_room_empties_room(ws_manager: WSManager):
    ws_manager.active[1] = MagicMock()
    ws_manager.rooms[10] = {1}

    ws_manager.remove_user_from_room(chat_id=10, user_id=1)

    assert 10 not in ws_manager.rooms


@pytest.mark.asyncio
async def test_broadcast_sends_to_recipients(ws_manager: WSManager):
    mock_ws1 = MagicMock()
    mock_ws1.send_json = AsyncMock()
    mock_ws2 = MagicMock()
    mock_ws2.send_json = AsyncMock()

    ws_manager.active = {1: mock_ws1, 2: mock_ws2}

    event = BaseEvent(type=TypeEvent.user_online, user_id=1)
    await ws_manager.broadcast(event=event, recipients={1, 2})

    mock_ws1.send_json.assert_awaited_once()
    mock_ws2.send_json.assert_awaited_once()


@pytest.mark.asyncio
async def test_broadcast_skips_disconnected(ws_manager: WSManager):
    mock_ws = MagicMock()
    mock_ws.send_json = AsyncMock()

    ws_manager.active = {1: mock_ws}

    event = BaseEvent(type=TypeEvent.user_online, user_id=1)
    await ws_manager.broadcast(event=event, recipients={1, 999})

    mock_ws.send_json.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_chat_users(ws_manager: WSManager):
    ws_manager.rooms[10] = {1, 2, 3}

    users = ws_manager.get_chat_users(chat_id=10)

    assert users == {1, 2, 3}


@pytest.mark.asyncio
async def test_get_chat_users_empty(ws_manager: WSManager):
    users = ws_manager.get_chat_users(chat_id=999)

    assert users == set()


@pytest.mark.asyncio
async def test_get_user_chats(ws_manager: WSManager):
    ws_manager.user_to_chats[1] = {10, 20}

    chats = ws_manager.get_user_chats(user_id=1)

    assert chats == {10, 20}
