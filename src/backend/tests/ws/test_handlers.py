import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import UserRole
from backend.services.core.services_container import ServicesContainer
from backend.ws.handler.chat import (
    ChatCreateHandler,
    ChatUpdateHandler,
    ChatDeleteHandler,
)
from backend.ws.handler.chat_participant import (
    ChatParticipantCreateHandler,
    ChatParticipantUpdateHandler,
    ChatParticipantDeleteHandler,
)
from backend.ws.handler.message import (
    MessageCreateHandler,
    MessageUpdateHandler,
    MessageDeleteHandler,
)
from backend.ws.handler.user import UserStartTypingHandler, UserStopTypingHandler
from backend.ws.schemas.events import (
    ChatCreateEvent,
    ChatUpdateEvent,
    ChatDeleteEvent,
    ChatParticipantCreateEvent,
    ChatParticipantUpdateEvent,
    ChatParticipantDeleteEvent,
    MessageCreateEvent,
    MessageUpdateEvent,
    MessageDeleteEvent,
    UserStartTypingEvent,
    UserStopTypingEvent,
    TypeEvent,
    ChatCreatedEvent,
    ChatUpdatedEvent,
    ChatDeletedEvent,
    ChatParticipantCreatedEvent,
    ChatParticipantUpdatedEvent,
    ChatParticipantDeletedEvent,
    MessageCreatedEvent,
    MessageUpdatedEvent,
    MessageDeletedEvent,
)

from ..conftest import (
    create_user_orm,
    create_chat_orm,
    create_participant_orm,
    create_message_orm,
)


@pytest.mark.asyncio
async def test_message_create_handler(
    services_container: ServicesContainer,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="handler_user")
    chat_orm = await create_chat_orm(db_session, name="Handler Chat")

    handler = MessageCreateHandler()
    event = MessageCreateEvent(
        message={"chat_id": chat_orm.id, "user_id": user_orm.id, "content": "Hello"},
    )

    result = await handler.handle(event=event, services=services_container)

    assert isinstance(result, MessageCreatedEvent)
    assert result.message.content == "Hello"


@pytest.mark.asyncio
async def test_message_update_handler(
    services_container: ServicesContainer,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="upd_handler_user")
    chat_orm = await create_chat_orm(db_session, name="Upd Handler Chat")
    msg_orm = await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Old"
    )

    handler = MessageUpdateHandler()
    event = MessageUpdateEvent(
        message={"id": msg_orm.id, "content": "Updated"},
    )

    result = await handler.handle(event=event, services=services_container)

    assert isinstance(result, MessageUpdatedEvent)
    assert result.message.content == "Updated"


@pytest.mark.asyncio
async def test_message_delete_handler(
    services_container: ServicesContainer,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="del_handler_user")
    chat_orm = await create_chat_orm(db_session, name="Del Handler Chat")
    msg_orm = await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Delete"
    )

    handler = MessageDeleteHandler()
    event = MessageDeleteEvent(
        message={
            "id": msg_orm.id,
            "chat_id": chat_orm.id,
            "user_id": user_orm.id,
            "content": "Delete",
            "created_at": "2024-01-01T00:00:00",
        },
    )

    result = await handler.handle(event=event, services=services_container)

    assert isinstance(result, MessageDeletedEvent)
    assert result.message.id == msg_orm.id


@pytest.mark.asyncio
async def test_chat_create_handler(
    services_container: ServicesContainer,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="chat_handler_user")

    handler = ChatCreateHandler()
    event = ChatCreateEvent(
        chat={"name": "New Chat", "is_group": False},
        participants=[{"chat_id": 0, "user_id": user_orm.id, "role": "member"}],
    )

    result = await handler.handle(event=event, services=services_container)

    assert isinstance(result, ChatCreatedEvent)
    assert result.chat.name == "New Chat"
    assert len(result.chat.participants) == 1


@pytest.mark.asyncio
async def test_chat_update_handler(
    services_container: ServicesContainer,
    db_session: AsyncSession,
):
    chat_orm = await create_chat_orm(db_session, name="Old Name")

    handler = ChatUpdateHandler()
    event = ChatUpdateEvent(
        chat={"id": chat_orm.id, "name": "Updated Name"},
    )

    result = await handler.handle(event=event, services=services_container)

    assert isinstance(result, ChatUpdatedEvent)
    assert result.chat.name == "Updated Name"


@pytest.mark.asyncio
async def test_chat_delete_handler(
    services_container: ServicesContainer,
    db_session: AsyncSession,
):
    chat_orm = await create_chat_orm(db_session, name="Delete Chat")

    handler = ChatDeleteHandler()
    event = ChatDeleteEvent(
        chat={
            "id": chat_orm.id,
            "name": "Delete Chat",
            "is_group": False,
            "created_at": "2024-01-01T00:00:00",
        },
    )

    result = await handler.handle(event=event, services=services_container)

    assert isinstance(result, ChatDeletedEvent)
    assert result.chat.id == chat_orm.id


@pytest.mark.asyncio
async def test_chat_participant_create_handler(
    services_container: ServicesContainer,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="part_handler_user")
    chat_orm = await create_chat_orm(db_session, name="Part Handler Chat")

    handler = ChatParticipantCreateHandler()
    event = ChatParticipantCreateEvent(
        chat_participant={
            "chat_id": chat_orm.id,
            "user_id": user_orm.id,
            "role": "member",
        },
    )

    result = await handler.handle(event=event, services=services_container)

    assert isinstance(result, ChatParticipantCreatedEvent)
    assert result.chat_participant.user_id == user_orm.id


@pytest.mark.asyncio
async def test_chat_participant_update_handler(
    services_container: ServicesContainer,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="upd_part_handler")
    chat_orm = await create_chat_orm(db_session, name="Upd Part Handler")
    part_orm = await create_participant_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, role=UserRole.member
    )

    handler = ChatParticipantUpdateHandler()
    event = ChatParticipantUpdateEvent(
        chat_participant={"id": part_orm.id, "role": "admin"},
    )

    result = await handler.handle(event=event, services=services_container)

    assert isinstance(result, ChatParticipantUpdatedEvent)
    assert result.chat_participant.user_id == user_orm.id


@pytest.mark.asyncio
async def test_chat_participant_delete_handler(
    services_container: ServicesContainer,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="del_part_handler")
    chat_orm = await create_chat_orm(db_session, name="Del Part Handler")
    part_orm = await create_participant_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id
    )

    handler = ChatParticipantDeleteHandler()
    event = ChatParticipantDeleteEvent(
        chat_participant={
            "id": part_orm.id,
            "chat_id": chat_orm.id,
            "user_id": user_orm.id,
            "role": "member",
            "joined_at": "2024-01-01T00:00:00",
        },
    )

    result = await handler.handle(event=event, services=services_container)

    assert isinstance(result, ChatParticipantDeletedEvent)
    assert result.chat_participant.id == part_orm.id


@pytest.mark.asyncio
async def test_user_start_typing_handler():
    handler = UserStartTypingHandler()
    event = UserStartTypingEvent(user_id=1, chat_id=10)

    result = await handler.handle(event=event, services=None)

    assert isinstance(result, UserStartTypingEvent)
    assert result.user_id == 1
    assert result.chat_id == 10


@pytest.mark.asyncio
async def test_user_stop_typing_handler():
    handler = UserStopTypingHandler()
    event = UserStopTypingEvent(user_id=1, chat_id=10)

    result = await handler.handle(event=event, services=None)

    assert isinstance(result, UserStopTypingEvent)
    assert result.user_id == 1
    assert result.chat_id == 10
