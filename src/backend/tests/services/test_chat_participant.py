import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import UserRole
from backend.services.chat_participant import ChatParticipantService
from backend.services.schemas.chat_participant import (
    ChatParticipantGet,
    ChatParticipantPatch,
    ChatParticipantPost,
)

from ..conftest import create_user_orm, create_chat_orm, create_participant_orm


@pytest.mark.asyncio
async def test_create_participant_success(
    chat_participant_service: ChatParticipantService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="part_user")
    chat_orm = await create_chat_orm(db_session, name="Part Chat")

    part_data = ChatParticipantPost(
        chat_id=chat_orm.id,
        user_id=user_orm.id,
        role=UserRole.member,
    )
    participant = await chat_participant_service.create_participant(
        chat_participant_data=part_data
    )

    assert participant.chat_id == chat_orm.id
    assert participant.user_id == user_orm.id


@pytest.mark.asyncio
async def test_create_participant_duplicate(
    chat_participant_service: ChatParticipantService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="dup_part_user")
    chat_orm = await create_chat_orm(db_session, name="Dup Chat")
    await create_participant_orm(db_session, chat_id=chat_orm.id, user_id=user_orm.id)

    part_data = ChatParticipantPost(
        chat_id=chat_orm.id,
        user_id=user_orm.id,
        role=UserRole.member,
    )

    with pytest.raises(HTTPException) as exc:
        await chat_participant_service.create_participant(
            chat_participant_data=part_data
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_get_all_chat_participants_multiple(
    chat_participant_service: ChatParticipantService,
    db_session: AsyncSession,
):
    user1 = await create_user_orm(db_session, uniq_name="part_a")
    user2 = await create_user_orm(db_session, uniq_name="part_b")
    chat_orm = await create_chat_orm(db_session, name="Multi Part Chat")
    await create_participant_orm(db_session, chat_id=chat_orm.id, user_id=user1.id)
    await create_participant_orm(db_session, chat_id=chat_orm.id, user_id=user2.id)

    participants = await chat_participant_service.get_all_chat_participants(
        chat_id=chat_orm.id
    )

    assert len(participants) == 2


@pytest.mark.asyncio
async def test_get_all_chat_participants_empty(
    chat_participant_service: ChatParticipantService,
    db_session: AsyncSession,
):
    chat_orm = await create_chat_orm(db_session, name="Empty Part Chat")

    participants = await chat_participant_service.get_all_chat_participants(
        chat_id=chat_orm.id
    )

    assert participants == []


@pytest.mark.asyncio
async def test_get_chat_participant_by_id_success(
    chat_participant_service: ChatParticipantService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="find_part_user")
    chat_orm = await create_chat_orm(db_session, name="Find Part Chat")
    part_orm = await create_participant_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id
    )

    participant = await chat_participant_service.get_chat_participant_by_id(
        chat_participant_id=part_orm.id
    )

    assert isinstance(participant, ChatParticipantGet)
    assert participant.user_id == user_orm.id


@pytest.mark.asyncio
async def test_get_chat_participant_by_id_not_found(
    chat_participant_service: ChatParticipantService,
):
    with pytest.raises(HTTPException) as exc:
        await chat_participant_service.get_chat_participant_by_id(
            chat_participant_id=99999
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_participant(
    chat_participant_service: ChatParticipantService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="update_part_user")
    chat_orm = await create_chat_orm(db_session, name="Update Part Chat")
    part_orm = await create_participant_orm(
        db_session,
        chat_id=chat_orm.id,
        user_id=user_orm.id,
        role=UserRole.member,
    )

    patch = ChatParticipantPatch(id=part_orm.id, role=UserRole.admin)
    updated = await chat_participant_service.update_participant(
        chat_participant_id=part_orm.id, chat_participant_data=patch
    )

    assert updated.role == UserRole.admin


@pytest.mark.asyncio
async def test_delete_participant_success(
    chat_participant_service: ChatParticipantService,
    db_session: AsyncSession,
):
    user_orm = await create_user_orm(db_session, uniq_name="del_part_user")
    chat_orm = await create_chat_orm(db_session, name="Del Part Chat")
    part_orm = await create_participant_orm(
        db_session, chat_id=chat_orm.id, user_id=user_orm.id
    )

    result = await chat_participant_service.delete_participant(
        chat_participant_id=part_orm.id
    )
    assert result is None

    with pytest.raises(HTTPException) as exc:
        await chat_participant_service.get_chat_participant_by_id(
            chat_participant_id=part_orm.id
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_participant_not_found(
    chat_participant_service: ChatParticipantService,
):
    with pytest.raises(HTTPException) as exc:
        await chat_participant_service.delete_participant(chat_participant_id=99999)
    assert exc.value.status_code == 404
