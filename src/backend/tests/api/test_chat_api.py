import pytest
from httpx import AsyncClient

from ..conftest import create_user_orm, create_chat_orm, create_participant_orm


@pytest.mark.asyncio
async def test_create_chat(async_client: AsyncClient):
    response = await async_client.post(
        "/chat/create",
        json={"name": "New Chat", "is_group": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Chat"


@pytest.mark.asyncio
async def test_get_chat_by_id(
    async_client: AsyncClient,
    db_session,
):
    chat_orm = await create_chat_orm(db_session, name="Test Chat")

    response = await async_client.get(f"/chat/get/{chat_orm.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Chat"


@pytest.mark.asyncio
async def test_get_chat_by_id_not_found(async_client: AsyncClient):
    response = await async_client.get("/chat/get/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_chats(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="chat_user")
    chat_orm = await create_chat_orm(db_session, name="My Chat")
    await create_participant_orm(db_session, chat_id=chat_orm.id, user_id=user_orm.id)

    response = await async_client.get("/chat/get", params={"user_id": user_orm.id})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "My Chat"


@pytest.mark.asyncio
async def test_update_chat(
    async_client: AsyncClient,
    db_session,
):
    chat_orm = await create_chat_orm(db_session, name="Old Name")

    response = await async_client.patch(
        f"/chat/{chat_orm.id}",
        json={"id": chat_orm.id, "name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_chat(
    async_client: AsyncClient,
    db_session,
):
    chat_orm = await create_chat_orm(db_session, name="Delete Me")

    response = await async_client.delete(f"/chat/{chat_orm.id}")
    assert response.status_code == 204
