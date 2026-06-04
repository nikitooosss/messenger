import pytest
from httpx import AsyncClient

from ..conftest import create_user_orm, create_chat_orm, create_message_orm


@pytest.mark.asyncio
async def test_create_message(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="msg_user")
    chat_orm = await create_chat_orm(db_session, name="Msg Chat")

    response = await async_client.post(
        "/message/create",
        json={
            "chat_id": chat_orm.id,
            "user_id": user_orm.id,
            "content": "Hello!",
        },
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Hello!"


@pytest.mark.asyncio
async def test_get_chat_messages(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="chat_msg_user")
    chat_orm = await create_chat_orm(db_session, name="Chat Msgs")
    await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Msg 1"
    )
    await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Msg 2"
    )

    response = await async_client.get(
        "/message/get",
        params={"limit": 10, "chat_id": chat_orm.id},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_message_by_id(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="find_msg_user")
    chat_orm = await create_chat_orm(db_session, name="Find Msg")
    msg_orm = await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Find me"
    )

    response = await async_client.get(f"/message/get/{msg_orm.id}")
    assert response.status_code == 200
    assert response.json()["content"] == "Find me"


@pytest.mark.asyncio
async def test_get_message_by_id_not_found(async_client: AsyncClient):
    response = await async_client.get("/message/get/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_message(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="upd_msg_user")
    chat_orm = await create_chat_orm(db_session, name="Upd Msg")
    msg_orm = await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Old"
    )

    response = await async_client.patch(
        f"/message/{msg_orm.id}",
        json={"id": msg_orm.id, "content": "Updated"},
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Updated"


@pytest.mark.asyncio
async def test_delete_message(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="del_msg_user")
    chat_orm = await create_chat_orm(db_session, name="Del Msg")
    msg_orm = await create_message_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id, content="Delete"
    )

    response = await async_client.delete(f"/message/{msg_orm.id}")
    assert response.status_code == 204
