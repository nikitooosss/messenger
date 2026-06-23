import logging

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
from backend.services.schemas.user import UserPublic
from backend.services.user import UserService

from .dispatcher import WSDispatcher
from .event_router import EventRouter
from .manager import WSManager
from .schemas.events import (
    PresenceRosterEvent,
    TypeEvent,
    UserOfflineEvent,
    UserOnlineEvent,
)
from .schemas.registry import parse_event
from .state_update import StateUpdater

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

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

    user_orm = await user_service.get_current_user(token=token)

    is_first_conn = await ws_manager.connect(user_id=user_orm.id, websocket=websocket)

    roster_event = PresenceRosterEvent(
        type=TypeEvent.presence_roster,
        user_ids=list(ws_manager.active.keys()),
    )
    await websocket.send_json(roster_event.model_dump(mode="json"))

    if is_first_conn:
        await services.user_service.update_is_active_to_true(user_id=user_orm.id)

        await ws_manager.init_online_user(
            user_id=user_orm.id, chat_service=services.chat_service
        )

        event = UserOnlineEvent(
            type=TypeEvent.user_online, user=UserPublic.model_validate(user_orm)
        )

        recipients = event_router.route(event=event, ws_manager=ws_manager)

        await ws_manager.broadcast(event=event, recipients=recipients)

    try:
        while True:
            data = await websocket.receive_json()
            try:
                event = parse_event(data)

                logger.info(f'EVENT WAS RECEIVE: {event}')

                created_event = await ws_dispatcher.dispatch(
                    event=event, services=services, user_id=user_orm.id
                )

                recipients = event_router.route(
                    event=created_event, ws_manager=ws_manager
                )

                await ws_manager.broadcast(event=created_event, recipients=recipients)

                await state_updater.update(
                    event=created_event,
                    ws_manager=ws_manager,
                    user_id=user_orm.id,
                )
            except Exception as inner_err:
                await ws_manager.broadcast_error(
                    user_id=user_orm.id, message=str(inner_err)
                )

    except WebSocketDisconnect:
        still_online = await ws_manager.disconnect(
            user_id=user_orm.id, websocket=websocket
        )
        if still_online:
            return

        await services.user_service.update_is_active_to_false(user_id=user_orm.id)
        await services.user_service.update_last_seen(user_id=user_orm.id)

        user_orm = await services.user_service.get_user_by_id(user_id=user_orm.id)

        event = UserOfflineEvent(
            type=TypeEvent.user_offline, user=UserPublic.model_validate(user_orm)
        )
        recipients = event_router.route(event=event, ws_manager=ws_manager)

        user_chats = list(ws_manager.get_user_chats(user_id=user_orm.id))

        for chat in user_chats:
            await ws_manager.remove_user_from_room(chat_id=chat, user_id=user_orm.id)

        await ws_manager.broadcast(event=event, recipients=recipients)


@router_ws.get("/state")
async def get_ws_state():
    return {
        "active": {
            user_id: {
                "connections": len(websockets),
                "sockets": [id(ws) for ws in websockets],
            }
            for user_id, websockets in ws_manager.active.items()
        },
        "rooms": {chat_id: list(users) for chat_id, users in ws_manager.rooms.items()},
        "user_to_chats": {
            user_id: list(chats) for user_id, chats in ws_manager.user_to_chats.items()
        },
    }
