from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import Response

from ...services.message import MessageService
from ...services.schemas.message import MessageGet, MessagePatch, MessagePost
from ..core.deps import get_message_service

router_message = APIRouter(
    prefix="/message",
    tags=["Message"],
)


@router_message.get("/get", response_model=list[MessageGet])
async def get_limit_chat_messages(
    service: Annotated[MessageService, Depends(get_message_service)],
    limit: int,
    chat_id: int,
):
    messages = await service.get_chat_messages(limit=limit, chat_id=chat_id)
    return messages


@router_message.get("/get/{message_id}", response_model=MessageGet)
async def get_message_by_id(
    service: Annotated[MessageService, Depends(get_message_service)],
    message_id: int,
):
    message = await service.get_message_by_id(message_id=message_id)
    return message


@router_message.post("/create", response_model=MessageGet)
async def create_message(
    service: Annotated[MessageService, Depends(get_message_service)],
    message_data: MessagePost,
):
    message = await service.create_message(message_data=message_data)
    return message


@router_message.patch("/{message_id}", response_model=MessagePatch)
async def update_message(
    service: Annotated[MessageService, Depends(get_message_service)],
    message_id: int,
    message_data: MessagePatch,
):
    message = await service.update_message(
        message_id=message_id, message_data=message_data
    )
    return message


@router_message.delete("/{message_id}", status_code=204)
async def delete_message(
    service: Annotated[MessageService, Depends(get_message_service)],
    message_id: int,
):
    await service.delete_message(message_id=message_id)

    return Response(status_code=204)
