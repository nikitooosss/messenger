from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import Chat, get_db
from api.schemas import ChatGet, ChatPatch, ChatPost

router_chat = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router_chat.get("/get", response_model=list[ChatGet])
async def get_all_chats(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Chat)
    result = await db.execute(stmt)
    chats = result.scalars().all()
    return chats


@router_chat.get("/get/{chat_id}", response_model=ChatGet)
async def get_chat_by_id(
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_id: int,
):
    stmt = select(Chat).where(Chat.id == chat_id)
    result = await db.execute(stmt)
    chat_orm = result.scalar_one_or_none()

    if chat_orm is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat = ChatGet.model_validate(chat_orm, from_attributes=True)

    return chat


@router_chat.post("/create", response_model=ChatPost)
async def create_chat(
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_data: ChatPost,
):
    chat = Chat(**chat_data.model_dump())

    db.add(chat)
    await db.commit()
    await db.refresh(chat)

    return chat


@router_chat.patch("/{chat_id}", response_model=ChatPatch)
async def update_chat(
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_id: int,
    chat_data: ChatPatch,
):
    stmt = select(Chat).where(Chat.id == chat_id)
    result = await db.execute(stmt)
    chat = result.scalar_one_or_none()

    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    update_data = chat_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(chat, field, value)

    await db.commit()
    await db.refresh(chat)

    return chat


@router_chat.delete("/{chat_id}", status_code=204)
async def delete_chat(
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_id: int,
):
    stmt = select(Chat).where(Chat.id == chat_id)
    result = await db.execute(stmt)
    chat = result.scalar_one_or_none()

    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    await db.delete(chat)
    await db.commit()
