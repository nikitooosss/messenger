import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.message import MessageService
from backend.services.schemas.message import MessageGet, MessagePatch, MessagePost

from ..conftest import create_user_orm, create_chat_orm, create_message_orm


@pytest.mark.asyncio
async def test_create_message(
    message_service: MessageService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="msg_user")
    chat_orm = await create_chat_orm(db_session, name="Msg Chat")

    msg_data = MessagePost(
        chat_id=chat_orm.id,
        user_id=user_orm.id,
        content="Test message",
    )
    msg = await message_service.create_message(message_data=msg_data)

    assert msg.content == "Test message"
    assert msg.chat_id == chat_orm.id
    assert msg.user_id == user_orm.id


@pytest.mark.asyncio
async def test_get_message_by_id_success(
    message_service: MessageService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="msg_user2")
    chat_orm = await create_chat_orm(db_session, name="Msg Chat 2")
    msg_orm = await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Find me"
    )

    msg = await message_service.get_message_by_id(message_id=msg_orm.id)

    assert isinstance(msg, MessageGet)
    assert msg.content == "Find me"


@pytest.mark.asyncio
async def test_get_message_by_id_not_found(message_service: MessageService):
    with pytest.raises(HTTPException) as exc:
        await message_service.get_message_by_id(message_id=99999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_chat_messages_with_limit(
    message_service: MessageService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="chat_msgs_user")
    chat_orm = await create_chat_orm(db_session, name="Chat Messages")
    for i in range(5):
        await create_message_orm(
            db_session,
            chat_id=chat_orm.id,
            user_id=user_orm.id,
            content=f"Message {i}",
        )

    messages = await message_service.get_chat_messages(limit=3, chat_id=chat_orm.id)

    assert len(messages) == 3


@pytest.mark.asyncio
async def test_get_chat_messages_empty(
    message_service: MessageService,
    db_session: AsyncSession,
):
    chat_orm = await create_chat_orm(db_session, name="Empty Chat")

    messages = await message_service.get_chat_messages(limit=10, chat_id=chat_orm.id)

    assert messages == []


@pytest.mark.asyncio
async def test_update_message(
    message_service: MessageService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="update_msg_user")
    chat_orm = await create_chat_orm(db_session, name="Update Chat")
    msg_orm = await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Old content"
    )

    patch = MessagePatch(id=msg_orm.id, content="Updated content")
    updated = await message_service.update_message(
        message_id=msg_orm.id, message_data=patch
    )

    assert updated.content == "Updated content"


@pytest.mark.asyncio
async def test_delete_message_success(
    message_service: MessageService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="del_msg_user")
    chat_orm = await create_chat_orm(db_session, name="Delete Chat")
    msg_orm = await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Delete me"
    )

    result = await message_service.delete_message(message_id=msg_orm.id)
    assert result is None

    with pytest.raises(HTTPException) as exc:
        await message_service.get_message_by_id(message_id=msg_orm.id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_message_not_found(message_service: MessageService):
    with pytest.raises(HTTPException) as exc:
        await message_service.delete_message(message_id=99999)
    assert exc.value.status_code == 404
