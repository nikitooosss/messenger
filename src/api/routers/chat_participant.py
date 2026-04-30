from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import ChatParticipant, get_db
from api.database.models import UserRole
from api.schemas import ChatParticipantGet, ChatParticipantPatch, ChatParticipantPost

router_chat_participant = APIRouter(
    prefix="/chat_participant",
    tags=["Chat participant"],
)


@router_chat_participant.get("/get", response_model=list[ChatParticipantGet])
async def get_all_participants(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(ChatParticipant)
    result = await db.execute(stmt)
    chat_participants = result.scalars().all()

    return chat_participants


@router_chat_participant.get(
    "/get/{chat_participant_id}", response_model=ChatParticipantGet
)
async def get_participant_by_id(
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_participant_id: int,
):
    stmt = select(ChatParticipant).where(ChatParticipant.id == chat_participant_id)
    result = await db.execute(stmt)
    chat_participant_orm = result.scalar_one_or_none()

    if chat_participant_orm is None:
        raise HTTPException(status_code=404, detail="Participant not found")

    chat_participant = ChatParticipantGet.model_validate(
        chat_participant_orm, from_attributes=True
    )

    return chat_participant


@router_chat_participant.post("/create", response_model=ChatParticipantPost)
async def create_participant(
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_participant_data: ChatParticipantPost,
    role: UserRole,
):
    stmt = select(ChatParticipant).where(
        ChatParticipant.user_id == chat_participant_data.user_id,
        ChatParticipant.chat_id == chat_participant_data.chat_id
    )
    result = await db.execute(stmt)
    participant = result.scalar_one_or_none()

    if participant is not None:
        raise HTTPException(status_code=409, detail="User already in chat")

    participant = ChatParticipant(**chat_participant_data.model_dump())
    participant.role = role

    db.add(participant)
    await db.commit()
    await db.refresh(participant)

    return participant


@router_chat_participant.patch(
    "/{chat_participant_id}", response_model=ChatParticipantPatch
)
async def update_participant(
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_participant_id: int,
    chat_participant_data: ChatParticipantPatch,
):
    stmt = select(ChatParticipant).where(ChatParticipant.id == chat_participant_id)
    result = await db.execute(stmt)
    chat_participant = result.scalar_one_or_none()

    if chat_participant is None:
        raise HTTPException(status_code=404, detail="Participant not found")

    update_data = chat_participant_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(chat_participant, field, value)

    await db.commit()
    await db.refresh(chat_participant)

    return chat_participant


@router_chat_participant.delete("/{chat_participant_id}", status_code=204)
async def delete_participant(
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_participant_id: int,
):
    stmt = select(ChatParticipant).where(ChatParticipant.id == chat_participant_id)
    result = await db.execute(stmt)
    chat = result.scalar_one_or_none()

    if chat is None:
        raise HTTPException(status_code=404, detail="ChatParticipant not found")

    await db.delete(chat)
    await db.commit()
