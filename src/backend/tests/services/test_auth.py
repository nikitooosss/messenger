import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.auth import UserRegister
from backend.services.auth import AuthService
from backend.services.core.password import hash_password

from ..conftest import create_user_orm


@pytest.mark.asyncio
async def test_register_user_success(auth_service: AuthService):
    user_data = UserRegister(
        uniq_name="newuser",
        name="New User",
        password_hash="plain_password",
    )
    user = await auth_service.register_user(user_data=user_data)

    assert user is not None
    assert user.uniq_name == "newuser"
    assert user.name == "New User"
    assert user.password_hash != "plain_password"


@pytest.mark.asyncio
async def test_register_user_duplicate(
    auth_service: AuthService,
    db_session: AsyncSession,
):
    await create_user_orm(db_session, uniq_name="dupuser")

    user_data = UserRegister(
        uniq_name="dupuser",
        password_hash="password",
    )
    user = await auth_service.register_user(user_data=user_data)

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_success(
    auth_service: AuthService,
    db_session: AsyncSession,
):
    hashed = hash_password("correct_password")
    await create_user_orm(
        db_session,
        uniq_name="logintest",
        password_hash=hashed,
    )

    user = await auth_service.authenticate_user(
        uniq_name="logintest",
        password="correct_password",
    )

    assert user is not None
    assert user.uniq_name == "logintest"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(
    auth_service: AuthService,
    db_session: AsyncSession,
):
    hashed = hash_password("correct_password")
    await create_user_orm(
        db_session,
        uniq_name="logintest2",
        password_hash=hashed,
    )

    user = await auth_service.authenticate_user(
        uniq_name="logintest2",
        password="wrong_password",
    )

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found(auth_service: AuthService):
    user = await auth_service.authenticate_user(
        uniq_name="nonexistent",
        password="password",
    )

    assert user is None
