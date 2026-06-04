from typing import Annotated

from fastapi import APIRouter, Response
from fastapi.params import Depends

from ...database.models import UserRole
from ...services.chat_participant import ChatParticipantService
from ...services.schemas.chat_participant import (
    ChatParticipantGet,
    ChatParticipantPatch,
    ChatParticipantPost,
)
from ..core.deps import get_chat_participant_service

router_chat_participant = APIRouter(
    prefix="/chat_participant",
    tags=["Chat participant"],
)


@router_chat_participant.get("/get", response_model=list[ChatParticipantGet])
async def get_all_chat_participants(
    service: Annotated[ChatParticipantService, Depends(get_chat_participant_service)],
    chat_id: int,
):
    chat_participants = await service.get_all_chat_participants(chat_id=chat_id)
    return chat_participants


@router_chat_participant.get(
    "/get/{chat_participant_id}", response_model=ChatParticipantGet
)
async def get_chat_participant_by_id(
    service: Annotated[ChatParticipantService, Depends(get_chat_participant_service)],
    chat_participant_id: int,
):
    chat_participant = await service.get_chat_participant_by_id(
        chat_participant_id=chat_participant_id
    )
    return chat_participant


@router_chat_participant.post("/create", response_model=ChatParticipantPost)
async def create_participant(
    service: Annotated[ChatParticipantService, Depends(get_chat_participant_service)],
    chat_participant_data: ChatParticipantPost,
):
    chat_participant = await service.create_participant(
        chat_participant_data=chat_participant_data
    )
    return chat_participant


@router_chat_participant.patch(
    "/{chat_participant_id}", response_model=ChatParticipantPatch
)
async def update_participant(
    service: Annotated[ChatParticipantService, Depends(get_chat_participant_service)],
    chat_participant_id: int,
    chat_participant_data: ChatParticipantPatch,
):
    chat_participant = await service.update_participant(
        chat_participant_id=chat_participant_id,
        chat_participant_data=chat_participant_data,
    )
    return chat_participant


@router_chat_participant.delete("/{chat_participant_id}", status_code=204)
async def delete_participant(
    service: Annotated[ChatParticipantService, Depends(get_chat_participant_service)],
    chat_participant_id: int,
):
    await service.delete_participant(chat_participant_id=chat_participant_id)
    return Response(status_code=204)
