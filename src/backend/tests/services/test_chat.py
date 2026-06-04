import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.chat import ChatService
from backend.services.schemas.chat import ChatGet, ChatPatch, ChatPost

from ..conftest import create_user_orm, create_chat_orm, create_participant_orm


@pytest.mark.asyncio
async def test_create_chat_success(chat_service: ChatService):
    chat_data = ChatPost(name="New Chat", is_group=False)
    chat = await chat_service.create_chat(chat_data=chat_data)

    assert chat.name == "New Chat"
    assert chat.is_group is False


@pytest.mark.asyncio
async def test_get_chat_by_id_success(
    chat_service: ChatService,
    db_session: AsyncSession,
):
    chat_orm = await create_chat_orm(db_session, name="Find Me")

    chat = await chat_service.get_chat_by_id(chat_id=chat_orm.id)

    assert isinstance(chat, ChatGet)
    assert chat.name == "Find Me"


@pytest.mark.asyncio
async def test_get_chat_by_id_not_found(chat_service: ChatService):
    with pytest.raises(HTTPException) as exc:
        await chat_service.get_chat_by_id(chat_id=99999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_chats_by_user_id_empty(
    chat_service: ChatService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="no_chats_user")

    chats = await chat_service.get_chats_by_user_id(user_id=user_orm.id)
    assert chats == []


@pytest.mark.asyncio
async def test_get_chats_by_user_id_multiple(
    chat_service: ChatService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="multi_chat_user")
    chat1 = await create_chat_orm(db_session, name="Chat 1")
    chat2 = await create_chat_orm(db_session, name="Chat 2")

    await create_participant_orm(db_session, chat_id=chat1.id, user_id=user_orm.id)
    await create_participant_orm(db_session, chat_id=chat2.id, user_id=user_orm.id)

    chats = await chat_service.get_chats_by_user_id(user_id=user_orm.id)
    assert len(chats) == 2


@pytest.mark.asyncio
async def test_update_chat(
    chat_service: ChatService,
    db_session: AsyncSession,
):
    chat_orm = await create_chat_orm(db_session, name="Old Name")

    patch = ChatPatch(id=chat_orm.id, name="New Name")
    updated = await chat_service.update_chat(chat_id=chat_orm.id, chat_data=patch)

    assert updated.name == "New Name"


@pytest.mark.asyncio
async def test_delete_chat_success(
    chat_service: ChatService,
    db_session: AsyncSession,
):
    chat_orm = await create_chat_orm(db_session, name="Delete Me")

    result = await chat_service.delete_chat(chat_id=chat_orm.id)
    assert result is None

    with pytest.raises(HTTPException) as exc:
        await chat_service.get_chat_by_id(chat_id=chat_orm.id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_chat_not_found(chat_service: ChatService):
    with pytest.raises(HTTPException) as exc:
        await chat_service.delete_chat(chat_id=99999)
    assert exc.value.status_code == 404
