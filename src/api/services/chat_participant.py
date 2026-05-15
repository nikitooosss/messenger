from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import ChatParticipant, UserRole, get_db
from api.database.models import Chat
from api.schemas import ChatParticipantGet, ChatParticipantPatch, ChatParticipantPost


class ChatParticipantService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db = db

    async def get_all_chat_participants(
        self,
        chat_id: int,
    ):
        stmt = select(ChatParticipant).join(Chat).where(Chat.id == chat_id)
        result = await self.db.execute(stmt)
        chat_participants = result.scalars().all()

        return chat_participants

    async def get_chat_participant_by_id(
        self,
        chat_participant_id: int,
    ):
        stmt = select(ChatParticipant).where(ChatParticipant.id == chat_participant_id)
        result = await self.db.execute(stmt)
        chat_participant_orm = result.scalar_one_or_none()

        if chat_participant_orm is None:
            raise HTTPException(status_code=404, detail="Participant not found")

        chat_participant = ChatParticipantGet.model_validate(
            chat_participant_orm, from_attributes=True
        )

        return chat_participant

    async def create_participant(
        self,
        chat_participant_data: ChatParticipantPost,
        role: UserRole,
    ):
        stmt = select(ChatParticipant).where(
            ChatParticipant.user_id == chat_participant_data.user_id,
            ChatParticipant.chat_id == chat_participant_data.chat_id,
        )
        result = await self.db.execute(stmt)
        chat_participant = result.scalar_one_or_none()

        if chat_participant is not None:
            raise HTTPException(status_code=409, detail="User already in chat")

        chat_participant = ChatParticipant(**chat_participant_data.model_dump())
        chat_participant.role = role

        self.db.add(chat_participant)
        await self.db.commit()
        await self.db.refresh(chat_participant)

        return chat_participant

    async def update_participant(
        self,
        chat_participant_id: int,
        chat_participant_data: ChatParticipantPatch,
    ):
        stmt = select(ChatParticipant).where(ChatParticipant.id == chat_participant_id)
        result = await self.db.execute(stmt)
        chat_participant = result.scalar_one_or_none()

        if chat_participant is None:
            raise HTTPException(status_code=404, detail="Participant not found")

        update_data = chat_participant_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(chat_participant, field, value)

        await self.db.commit()
        await self.db.refresh(chat_participant)

        return chat_participant

    async def delete_participant(
        self,
        chat_participant_id: int,
    ):
        stmt = select(ChatParticipant).where(ChatParticipant.id == chat_participant_id)
        result = await self.db.execute(stmt)
        chat = result.scalar_one_or_none()

        if chat is None:
            raise HTTPException(status_code=404, detail="ChatParticipant not found")

        await self.db.delete(chat)
        await self.db.commit()

        return None
