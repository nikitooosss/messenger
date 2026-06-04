from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.schemas import (
    ChatParticipantGet,
    ChatParticipantPatch,
    ChatParticipantPost,
)

from ..database.get_db import get_db
from ..database.models import Chat, ChatParticipant


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

    async def _get_participant_orm_by_id(
        self, chat_participant_id: int
    ) -> ChatParticipant:
        stmt = select(ChatParticipant).where(ChatParticipant.id == chat_participant_id)
        result = await self.db.execute(stmt)
        participant = result.scalar_one_or_none()

        if participant is None:
            raise HTTPException(status_code=404, detail="Participant not found")

        return participant

    async def create_participant(
        self,
        chat_participant_data: ChatParticipantPost,
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

        self.db.add(chat_participant)
        await self.db.commit()
        await self.db.refresh(chat_participant)

        return chat_participant

    async def update_participant(
        self,
        chat_participant_id: int,
        chat_participant_data: ChatParticipantPatch,
    ):
        chat_participant = await self._get_participant_orm_by_id(
            chat_participant_id=chat_participant_id
        )

        update_data = chat_participant_data.model_dump(
            exclude_unset=True, exclude={"id"}
        )

        for field, value in update_data.items():
            setattr(chat_participant, field, value)

        await self.db.commit()
        await self.db.refresh(chat_participant)

        return chat_participant

    async def delete_participant(
        self,
        chat_participant_id: int,
    ):
        participant = await self._get_participant_orm_by_id(chat_participant_id)

        await self.db.delete(participant)
        await self.db.commit()

        return None
