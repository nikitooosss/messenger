from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import Chat, ChatParticipant, get_db
from api.schemas import ChatGet, ChatPatch, ChatPost


class ChatService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db = db

    async def get_all_user_chats(
        self,
        user_id: int,
    ):
        stmt = (
            select(Chat)
            .join(ChatParticipant)
            .filter(ChatParticipant.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        chats = result.scalars().all()

        return chats

    async def get_chat_by_id(
        self,
        chat_id: int,
    ):
        stmt = select(Chat).where(Chat.id == chat_id)
        result = await self.db.execute(stmt)
        chat_orm = result.scalar_one_or_none()

        if chat_orm is None:
            raise HTTPException(status_code=404, detail="Chat not found")

        chat = ChatGet.model_validate(chat_orm, from_attributes=True)

        return chat

    async def create_chat(
        self,
        chat_data: ChatPost,
    ):
        chat = Chat(**chat_data.model_dump())

        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)

        return chat

    async def update_chat(
        self,
        chat_id: int,
        chat_data: ChatPatch,
    ):
        stmt = select(Chat).where(Chat.id == chat_id)
        result = await self.db.execute(stmt)
        chat = result.scalar_one_or_none()

        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")

        update_data = chat_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(chat, field, value)

        await self.db.commit()
        await self.db.refresh(chat)

        return chat

    async def delete_chat(
        self,
        chat_id: int,
    ):
        stmt = select(Chat).where(Chat.id == chat_id)
        result = await self.db.execute(stmt)
        chat = result.scalar_one_or_none()

        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")

        await self.db.delete(chat)
        await self.db.commit()

        return None
