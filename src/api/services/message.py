from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import Message, get_db
from api.schemas import MessageGet, MessagePatch, MessagePost


class MessageService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        self.db = db

    async def get_chat_messages(
        self,
        limit: int,
        chat_id: int,
    ):
        stmt = select(Message).limit(limit).where(Message.chat_id == chat_id)
        result = await self.db.execute(stmt)
        messages = result.scalars().all()

        return messages

    async def get_message_by_id(
        self,
        message_id: int,
    ):
        stmt = select(Message).where(Message.id == message_id)
        result = await self.db.execute(stmt)
        message_orm = result.scalar_one_or_none()

        if message_orm is None:
            raise HTTPException(status_code=404, detail="Message not found")

        message = MessageGet.model_validate(message_orm, from_attributes=True)
        return message

    async def create_message(
        self,
        message_data: MessagePost,
    ):
        message = Message(**message_data.model_dump())

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def change_message(
        self,
        message_id: int,
        message_data: MessagePatch,
    ):
        stmt = select(Message).where(Message.id == message_id)

        result = await self.db.execute(stmt)
        message = result.scalar_one_or_none()

        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")

        update_data = message_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(message, field, value)

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def delete_message(
        self,
        message_id: int,
    ):
        stmt = select(Message).where(Message.id == message_id)
        result = await self.db.execute(stmt)
        message = result.scalar_one_or_none()

        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")

        await self.db.delete(message)
        await self.db.commit()

        return None
