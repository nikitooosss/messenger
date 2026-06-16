from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..database.get_db import get_db
from ..database.models import Chat, ChatParticipant, User
from .schemas import ChatGet, ChatPatch, ChatPost, ChatWithDisplayName


class ChatService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db = db

    async def get_chats_by_user_id(
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

    async def _get_chat_orm_by_id(self, chat_id: int) -> Chat:
        stmt = select(Chat).where(Chat.id == chat_id)
        result = await self.db.execute(stmt)
        chat = result.scalar_one_or_none()

        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")

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
        chat = await self._get_chat_orm_by_id(chat_id=chat_id)

        update_data = chat_data.model_dump(
            exclude_unset=True,
            exclude={"id"},
        )

        for field, value in update_data.items():
            setattr(chat, field, value)

        await self.db.commit()
        await self.db.refresh(chat)

        return chat

    async def delete_chat(
        self,
        chat_id: int,
    ):
        chat = await self._get_chat_orm_by_id(chat_id)

        await self.db.delete(chat)
        await self.db.commit()

        return None

    async def search_chats(
        self,
        user_id: int,
        query: Optional[str] = None,
    ) -> list[ChatWithDisplayName]:
        stmt = (
            select(Chat)
            .join(ChatParticipant)
            .options(joinedload(Chat.participants).joinedload(ChatParticipant.user))
            .filter(ChatParticipant.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        chats = result.unique().scalars().all()

        chat_results = []
        for chat in chats:
            display_name = chat.name

            if not chat.is_group:
                peer = next(
                    (p for p in chat.participants if p.user_id != user_id),
                    None,
                )
                if peer and peer.user:
                    display_name = peer.user.name or peer.user.uniq_name

            if query and query.lower() not in display_name.lower():
                continue

            chat_results.append(
                ChatWithDisplayName(
                    id=chat.id,
                    name=chat.name,
                    is_group=chat.is_group,
                    created_at=chat.created_at,
                    display_name=display_name,
                )
            )

        return chat_results
