from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.params import Depends

from backend.api.core.deps import (
    get_chat_participant_service,
    get_chat_service,
    get_message_service,
    get_user_service,
)
from backend.services.chat import ChatService
from backend.services.chat_participant import ChatParticipantService
from backend.services.core.services_container import ServicesContainer
from backend.services.message import MessageService
from backend.services.schemas.user import UserGet
from backend.services.user import UserService

from .dispatcher import WSDispatcher
from .manager import WSManager
from .router import EventRouter
from .schemas.events import BaseEvent, TypeEvent, UserOfflineEvent, UserOnlineEvent
from .state_update import StateUpdater

router_ws = APIRouter(
    prefix="/ws",
    tags=["WebSocket"],
)

ws_manager = WSManager()
ws_dispatcher = WSDispatcher()
event_router = EventRouter()
state_updater = StateUpdater()


@router_ws.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    user_service: Annotated[UserService, Depends(get_user_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    message_service: Annotated[MessageService, Depends(get_message_service)],
    chat_participant_service: Annotated[
        ChatParticipantService, Depends(get_chat_participant_service)
    ],
):
    services = ServicesContainer(
        chat_service=chat_service,
        message_service=message_service,
        chat_participant_service=chat_participant_service,
        user_service=user_service,
    )

    token = websocket.cookies.get("access_token")

    if token is None:
        await websocket.close(code=1008)
        return

    user = await user_service.get_current_user(token=token)

    await ws_manager.connect(
        user_id=user.id, websocket=websocket, chat_service=chat_service
    )

    await services.user_service.update_is_active_on_opposite(user_id=user.id)

    event = UserOnlineEvent(type=TypeEvent.user_online, user_id=user.id)
    recipients = event_router.route(event=event, ws_manager=ws_manager)

    await ws_manager.broadcast(event=event, recipients=recipients)

    try:
        while True:
            data = await websocket.receive_json()
            event = BaseEvent.model_validate(data)
            created_event = await ws_dispatcher.dispatch(event=event, services=services)

            state_updater.update(
                event=created_event,
                ws_manager=ws_manager,
            )

            recipients = event_router.route(event=created_event, ws_manager=ws_manager)

            await ws_manager.broadcast(event=created_event, recipients=recipients)

    except WebSocketDisconnect:
        await services.user_service.update_is_active_on_opposite(user_id=user.id)

        user_orm = await services.user_service.update_last_seen(user_id=user.id)
        user = UserGet.model_validate(user_orm)

        event = UserOfflineEvent(type=TypeEvent.user_offline, user=user)
        recipients = event_router.route(event=event, ws_manager=ws_manager)

        await ws_manager.disconnect(user_id=user.id)

        await ws_manager.broadcast(event=event, recipients=recipients)


@router_ws.get("/state")
async def get_ws_state():
    return {
        "active": list(ws_manager.active.keys()),
        "rooms": {chat_id: list(users) for chat_id, users in ws_manager.rooms.items()},
        "user_to_chats": {
            user_id: list(chats) for user_id, chats in ws_manager.user_to_chats.items()
        },
    }
