import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.core.password import hash_password
from backend.services.schemas.user import UserGet, UserPatch, UserPost
from backend.services.user import UserService

from ..conftest import create_user_orm


@pytest.mark.asyncio
async def test_create_user_success(
    user_service: UserService,
    db_session: AsyncSession,
):
    user_data = UserPost(
        uniq_name="newuser",
        name="New User",
        password_hash="plain_password",
    )
    user = await user_service.create_user(user_data=user_data)

    assert user.uniq_name == "newuser"
    assert user.name == "New User"
    assert user.password_hash != "plain_password"


@pytest.mark.asyncio
async def test_create_user_duplicate(
    user_service: UserService,
    db_session: AsyncSession,
):
    await create_user_orm(db_session, uniq_name="dupuser")

    user_data = UserPost(
        uniq_name="dupuser",
        password_hash="password",
    )

    with pytest.raises(HTTPException) as exc:
        await user_service.create_user(user_data=user_data)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_get_all_users_empty(user_service: UserService):
    users = await user_service.get_all_users()
    assert users == []


@pytest.mark.asyncio
async def test_get_all_users_multiple(
    user_service: UserService,
    db_session: AsyncSession,
):
    await create_user_orm(db_session, uniq_name="user_a")
    await create_user_orm(db_session, uniq_name="user_b")

    users = await user_service.get_all_users()
    assert len(users) == 2


@pytest.mark.asyncio
async def test_get_user_by_id_success(
    user_service: UserService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="findme")

    user = await user_service.get_user_by_id(user_id=user_orm.id)

    assert isinstance(user, UserGet)
    assert user.uniq_name == "findme"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service: UserService):
    with pytest.raises(HTTPException) as exc:
        await user_service.get_user_by_id(user_id=99999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_user(
    user_service: UserService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="update_me")

    patch = UserPatch(name="Updated Name")
    updated = await user_service.update_user(user_id=user_orm.id, user_data=patch)

    assert updated.name == "Updated Name"


@pytest.mark.asyncio
async def test_delete_user_success(
    user_service: UserService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="delete_me")

    result = await user_service.delete_user(user_id=user_orm.id)
    assert result is None

    remaining = await user_service.get_all_users()
    assert len(remaining) == 0


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service: UserService):
    with pytest.raises(HTTPException) as exc:
        await user_service.delete_user(user_id=99999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_last_seen(
    user_service: UserService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="last_seen_test")

    import datetime

    original = user_orm.last_seen

    updated = await user_service.update_last_seen(user_id=user_orm.id)

    assert updated.last_seen >= original


@pytest.mark.asyncio
async def test_update_is_active_to_true(
    user_service: UserService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(
        db_session, uniq_name="active_true_test", is_active=False
    )

    await user_service.update_is_active_to_true(user_id=user_orm.id)

    await db_session.refresh(user_orm)
    assert user_orm.is_active is True


@pytest.mark.asyncio
async def test_update_is_active_to_false(
    user_service: UserService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(
        db_session, uniq_name="active_false_test", is_active=True
    )

    await user_service.update_is_active_to_false(user_id=user_orm.id)

    await db_session.refresh(user_orm)
    assert user_orm.is_active is False


@pytest.mark.asyncio
async def test_reset_all_is_active(
    user_service: UserService,
    db_session: AsyncSession,
):
    a = await create_user_orm(db_session, uniq_name="reset_a", is_active=True)
    b = await create_user_orm(db_session, uniq_name="reset_b", is_active=True)

    await user_service.reset_all_is_active()

    await db_session.refresh(a)
    await db_session.refresh(b)
    assert a.is_active is False
    assert b.is_active is False


@pytest.mark.asyncio
async def test_reset_all_is_active_no_users(
    user_service: UserService,
    db_session: AsyncSession,
):
    await user_service.reset_all_is_active()

    users = await user_service.get_all_users()
    assert users == []
