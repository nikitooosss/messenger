from typing import Annotated

from fastapi import APIRouter, Response
from fastapi.params import Depends

from api.core import get_chat_service
from api.schemas import ChatGet, ChatPatch, ChatPost
from api.services import ChatService

router_chat = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router_chat.get("/get", response_model=list[ChatGet])
async def get_all_user_chats(
    service: Annotated[ChatService, Depends(get_chat_service)],
    user_id: int,
):
    chats = await service.get_all_user_chats(user_id=user_id)
    return chats


@router_chat.get("/get/{chat_id}", response_model=ChatGet)
async def get_chat_by_id(
    service: Annotated[ChatService, Depends(get_chat_service)],
    chat_id: int,
):
    chat = await service.get_chat_by_id(chat_id=chat_id)
    return chat


@router_chat.post("/create", response_model=ChatPost)
async def create_chat(
    service: Annotated[ChatService, Depends(get_chat_service)],
    chat_data: ChatPost,
):
    chat = await service.create_chat(chat_data=chat_data)
    return chat


@router_chat.patch("/{chat_id}", response_model=ChatPatch)
async def update_chat(
    service: Annotated[ChatService, Depends(get_chat_service)],
    chat_id: int,
    chat_data: ChatPatch,
):
    chat = await service.update_chat(chat_id=chat_id, chat_data=chat_data)
    return chat


@router_chat.delete("/{chat_id}", status_code=204)
async def delete_chat(
    service: Annotated[ChatService, Depends(get_chat_service)],
    chat_id: int,
):
    await service.delete_chat(chat_id=chat_id)
    return Response(status_code=204)
