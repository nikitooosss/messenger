import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    response = await async_client.post(
        "/auth/register",
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
async def test_register_duplicate(
    async_client: AsyncClient,
):
    await async_client.post(
        "/auth/register",
        json={
            "uniq_name": "dupuser",
            "password_hash": "secret",
        },
    )
    response = await async_client.post(
        "/auth/register",
        json={
            "uniq_name": "dupuser",
            "password_hash": "secret",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    await async_client.post(
        "/auth/register",
        json={
            "uniq_name": "loginuser",
            "password_hash": "correct_password",
        },
    )
    response = await async_client.post(
        "/auth/login",
        data={"username": "loginuser", "password": "correct_password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient):
    await async_client.post(
        "/auth/register",
        json={
            "uniq_name": "badpwuser",
            "password_hash": "correct_password",
        },
    )
    response = await async_client.post(
        "/auth/login",
        data={"username": "badpwuser", "password": "wrong_password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
