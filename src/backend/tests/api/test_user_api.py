import pytest
from httpx import AsyncClient

from backend.services.core.password import hash_password

from ..conftest import create_user_orm


@pytest.mark.asyncio
async def test_get_all_users_empty(async_client: AsyncClient):
    response = await async_client.get("/user/get")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_users_multiple(
    async_client: AsyncClient,
    db_session,
):
    await create_user_orm(db_session, uniq_name="user_a")
    await create_user_orm(db_session, uniq_name="user_b")

    response = await async_client.get("/user/get")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_user_by_id(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="findme")

    response = await async_client.get(f"/user/get/{user_orm.id}")
    assert response.status_code == 200
    assert response.json()["uniq_name"] == "findme"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(async_client: AsyncClient):
    response = await async_client.get("/user/get/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    response = await async_client.post(
        "/user/create",
        json={
            "uniq_name": "newuser",
            "name": "New User",
            "password_hash": "secret",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["uniq_name"] == "newuser"


@pytest.mark.asyncio
async def test_create_user_duplicate(
    async_client: AsyncClient,
    db_session,
):
    await create_user_orm(db_session, uniq_name="dupuser")

    response = await async_client.post(
        "/user/create",
        json={
            "uniq_name": "dupuser",
            "password_hash": "secret",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_user(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="update_me")

    response = await async_client.patch(
        f"/user/{user_orm.id}",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_user(
    async_client: AsyncClient,
    db_session,
):
    user_orm = await create_user_orm(db_session, uniq_name="delete_me")

    response = await async_client.delete(f"/user/{user_orm.id}")
    assert response.status_code == 204
