from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import Message, get_db
from api.schemas import MessageGet, MessagePatch, MessagePost

router_message = APIRouter(
    prefix="/message",
    tags=["Message"],
)


@router_message.get("/get", response_model=list[MessageGet])
async def get_all_messages(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Message)
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return messages


@router_message.get("/get/{message_id}", response_model=MessageGet)
async def get_message_by_id(
    db: Annotated[AsyncSession, Depends(get_db)],
    message_id: int,
):
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    message_orm = result.scalar_one_or_none()

    if message_orm is None:
        raise HTTPException(status_code=404, detail="Message not found")

    message = MessageGet.model_validate(message_orm, from_attributes=True)

    return message


@router_message.post("/create", response_model=MessagePost)
async def create_message(
    db: Annotated[AsyncSession, Depends(get_db)],
    message_data: MessagePost,
):
    message = Message(**message_data.model_dump())

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message


@router_message.patch("/{message_id}", response_model=MessagePatch)
async def update_message(
    db: Annotated[AsyncSession, Depends(get_db)],
    message_id: int,
    message_data: MessagePatch,
):
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    message = result.scalar_one_or_none()

    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    update_data = message_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(message, field, value)

    await db.commit()
    await db.refresh(message)

    return message


@router_message.delete("/{message_id}", status_code=204)
async def delete_message(
    db: Annotated[AsyncSession, Depends(get_db)],
    message_id: int,
):
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    chat = result.scalar_one_or_none()

    if chat is None:
        raise HTTPException(status_code=404, detail="Message not found")

    await db.delete(chat)
    await db.commit()
