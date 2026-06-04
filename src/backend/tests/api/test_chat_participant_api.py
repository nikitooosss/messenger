import pytest
from httpx import AsyncClient

from ..conftest import create_user_orm, create_chat_orm, create_participant_orm


@pytest.mark.asyncio
async def test_create_participant(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="part_user")
    chat_orm = await create_chat_orm(db_session, name="Part Chat")

    response = await async_client.post(
        "/chat_participant/create",
        json={
            "chat_id": chat_orm.id,
            "user_id": user_orm.id,
            "role": "member",
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_chat_participants(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="list_part_user")
    chat_orm = await create_chat_orm(db_session, name="List Parts")
    await create_participant_orm(db_session, chat_id=chat_orm.id, user_id=user_orm.id)

    response = await async_client.get(
        "/chat_participant/get",
        params={"chat_id": chat_orm.id},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_participant_by_id(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="find_part")
    chat_orm = await create_chat_orm(db_session, name="Find Part")
    part_orm = await create_participant_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id
    )

    response = await async_client.get(f"/chat_participant/get/{part_orm.id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_participant_by_id_not_found(async_client: AsyncClient):
    response = await async_client.get("/chat_participant/get/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_participant(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="upd_part")
    chat_orm = await create_chat_orm(db_session, name="Upd Part")
    part_orm = await create_participant_orm(
        db_session,
        chat_id=chat_orm.id,
        user_id=user_orm.id,
    )

    response = await async_client.patch(
        f"/chat_participant/{part_orm.id}",
        json={"id": part_orm.id, "role": "admin"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_participant(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="del_part")
    chat_orm = await create_chat_orm(db_session, name="Del Part")
    part_orm = await create_participant_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id
    )

    response = await async_client.delete(f"/chat_participant/{part_orm.id}")
    assert response.status_code == 204
