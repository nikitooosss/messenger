from datetime import datetime
from unittest.mock import MagicMock

from backend.database.models import UserRole
from backend.ws.manager import WSManager
from backend.ws.schemas.events import (
    ChatCreatedEvent,
    ChatDeletedEvent,
    ChatParticipantCreatedEvent,
    ChatParticipantDeletedEvent,
    ChatDetails,
    ChatDelete,
    ChatParticipantGet,
    ChatParticipantDelete,
    MessageCreatedEvent,
    TypeEvent,
    MessageGet,
)
from backend.ws.state_update import StateUpdater


def _make_ws_manager():
    mgr = WSManager()
    mgr.active = {1: MagicMock(), 2: MagicMock()}
    mgr.user_to_chats = {1: set()}
    return mgr


def _make_participant_ref(user_id: int):
    return ChatParticipantGet(
        id=user_id,
        chat_id=10,
        user_id=user_id,
        role=UserRole.member,
        joined_at=datetime.now(),
    )


def test_chat_created_updates_rooms():
    mgr = _make_ws_manager()
    updater = StateUpdater()

    participants = [_make_participant_ref(1), _make_participant_ref(2)]

    event = ChatCreatedEvent(
        chat=ChatDetails(
            id=10,
            name="New Chat",
            is_group=False,
            created_at=datetime.now(),
            participants=participants,
        ),
        participants=participants,
    )

    updater.update(event=event, ws_manager=mgr)

    assert 10 in mgr.rooms
    assert mgr.rooms[10] == {1, 2}


def test_chat_deleted_removes_room():
    mgr = _make_ws_manager()
    mgr.rooms[10] = {1, 2}
    mgr.user_to_chats[1] = {10}
    mgr.user_to_chats[2] = {10}
    updater = StateUpdater()

    participants = [_make_participant_ref(1), _make_participant_ref(2)]

    event = ChatDeletedEvent(
        chat=ChatDelete(id=10),
        participants=participants,
    )

    updater.update(event=event, ws_manager=mgr)

    assert 10 not in mgr.rooms
    assert 10 not in mgr.user_to_chats.get(1, set())


def test_chat_participant_created_adds_user_to_room():
    mgr = _make_ws_manager()
    updater = StateUpdater()

    event = ChatParticipantCreatedEvent(
        chat_participant=ChatParticipantGet(
            id=1,
            chat_id=10,
            user_id=1,
            role=UserRole.member,
            joined_at=datetime.now(),
        ),
    )

    updater.update(event=event, ws_manager=mgr)

    assert mgr.rooms[10] == {1}
    assert 10 in mgr.user_to_chats[1]


def test_chat_participant_deleted_removes_user():
    mgr = _make_ws_manager()
    mgr.rooms[10] = {1, 2}
    mgr.user_to_chats[1] = {10}
    updater = StateUpdater()

    event = ChatParticipantDeletedEvent(
        chat_participant=ChatParticipantDelete(id=1, chat_id=10, user_id=1),
    )

    updater.update(event=event, ws_manager=mgr)

    assert mgr.rooms[10] == {2}


def test_irrelevant_event_is_noop():
    mgr = _make_ws_manager()
    updater = StateUpdater()

    event = MessageCreatedEvent(
        message=MessageGet(
            id=1, chat_id=10, user_id=1, content="Hi", created_at=datetime.now()
        ),
    )

    updater.update(event=event, ws_manager=mgr)
    # No error should occur
