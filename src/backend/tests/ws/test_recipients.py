from datetime import datetime

from backend.database.models import UserRole
from backend.ws.manager import WSManager
from backend.ws.recipients.chat import ChatRecipients
from backend.ws.recipients.chat_participant import ChatParticipantRecipients
from backend.ws.recipients.message import MessageRecipients
from backend.ws.recipients.user import UserTypingRecipients, UserPresenceRecipients
from backend.ws.schemas.events import (
    MessageCreatedEvent,
    ChatCreatedEvent,
    ChatParticipantCreatedEvent,
    UserStartTypingEvent,
    UserOnlineEvent,
    TypeEvent,
    ChatDetails,
    ChatParticipantGet,
    MessageGet,
)


def _make_ws_manager():
    mgr = WSManager()
    mgr.rooms = {10: {1, 2, 3}, 20: {4, 5}}
    mgr.user_to_chats = {1: {10, 20}, 2: {10}}
    return mgr


def test_message_recipients():
    mgr = _make_ws_manager()
    event = MessageCreatedEvent(
        message=MessageGet(
            id=1, chat_id=10, user_id=1, content="Hi", created_at=datetime.now()
        ),
    )
    recipients = MessageRecipients().resolve(event, mgr)
    assert recipients == {1, 2, 3}


def test_chat_recipients():
    mgr = _make_ws_manager()
    event = ChatCreatedEvent(
        chat=ChatDetails(
            id=10,
            name="Test",
            is_group=False,
            created_at=datetime.now(),
            participants=[],
        ),
        participants=[],
    )
    recipients = ChatRecipients().resolve(event, mgr)
    assert recipients == {1, 2, 3}


def test_chat_participant_recipients():
    mgr = _make_ws_manager()
    event = ChatParticipantCreatedEvent(
        chat_participant=ChatParticipantGet(
            id=1,
            chat_id=10,
            user_id=1,
            role=UserRole.member,
            joined_at=datetime.now(),
        ),
    )
    recipients = ChatParticipantRecipients().resolve(event, mgr)
    assert recipients == {1, 2, 3}


def test_user_typing_recipients():
    mgr = _make_ws_manager()
    event = UserStartTypingEvent(user_id=1, chat_id=10)
    recipients = UserTypingRecipients().resolve(event, mgr)
    assert recipients == {1, 2, 3}


def test_user_presence_recipients_excludes_self():
    mgr = _make_ws_manager()
    event = UserOnlineEvent(user_id=1)
    recipients = UserPresenceRecipients().resolve(event, mgr)
    assert 1 not in recipients
    assert recipients == {2, 3, 4, 5}


def test_user_presence_no_duplicates():
    mgr = _make_ws_manager()
    event = UserOnlineEvent(user_id=2)
    recipients = UserPresenceRecipients().resolve(event, mgr)
    assert recipients == {1, 3}
