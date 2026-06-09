import enum

from pydantic.main import BaseModel

from backend.services.schemas.chat import (
    ChatDelete,
    ChatDetails,
    ChatGet,
    ChatPatch,
    ChatPost,
)
from backend.services.schemas.chat_participant import (
    ChatParticipantDelete,
    ChatParticipantGet,
    ChatParticipantPatch,
    ChatParticipantPost,
)
from backend.services.schemas.message import (
    MessageDelete,
    MessageGet,
    MessagePatch,
    MessagePost,
)
from backend.services.schemas.user import UserGet


class TypeEvent(enum.Enum):
    message_create = "message_create"
    message_created = "message_created"

    message_update = "message_update"
    message_updated = "message_updated"

    message_delete = "message_delete"
    message_deleted = "message_deleted"

    chat_create = "chat_create"
    chat_created = "chat_created"

    chat_update = "chat_update"
    chat_updated = "chat_updated"

    chat_delete = "chat_delete"
    chat_deleted = "chat_deleted"

    chat_participant_create = "chat_participant_create"
    chat_participant_created = "chat_participant_created"

    chat_participant_update = "chat_participant_update"
    chat_participant_updated = "chat_participant_updated"

    chat_participant_delete = "chat_participant_delete"
    chat_participant_deleted = "chat_participant_deleted"

    user_start_typing = "user_start_typing"
    user_stop_typing = "user_stop_typing"

    user_online = "user_online"
    user_offline = "user_offline"


class BaseEvent(BaseModel):
    type: TypeEvent


class MessageCreateEvent(BaseEvent):
    type: TypeEvent = TypeEvent.message_create
    message: MessagePost


class MessageCreatedEvent(BaseEvent):
    type: TypeEvent = TypeEvent.message_created
    message: MessageGet


class MessageUpdateEvent(BaseEvent):
    type: TypeEvent = TypeEvent.message_update
    message: MessagePatch


class MessageUpdatedEvent(BaseEvent):
    type: TypeEvent = TypeEvent.message_updated
    message: MessageGet


class MessageDeleteEvent(BaseEvent):
    type: TypeEvent = TypeEvent.message_delete
    message: MessageGet


class MessageDeletedEvent(BaseEvent):
    type: TypeEvent = TypeEvent.message_deleted
    message: MessageDelete


class ChatCreateEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_create
    chat: ChatPost

    participants: list[ChatParticipantPost]


class ChatCreatedEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_created
    chat: ChatDetails
    participants: list[ChatParticipantGet]


class ChatUpdateEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_update
    chat: ChatPatch


class ChatUpdatedEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_updated
    chat: ChatGet


class ChatDeleteEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_delete
    chat: ChatGet


class ChatDeletedEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_deleted
    chat: ChatDelete
    participants: list[ChatParticipantGet]


class ChatParticipantCreateEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_participant_create
    chat_participant: ChatParticipantPost


class ChatParticipantCreatedEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_participant_created
    chat_participant: ChatParticipantGet


class ChatParticipantUpdateEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_participant_update
    chat_participant: ChatParticipantPatch


class ChatParticipantUpdatedEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_participant_updated
    chat_participant: ChatParticipantGet


class ChatParticipantDeleteEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_participant_delete
    chat_participant: ChatParticipantGet


class ChatParticipantDeletedEvent(BaseEvent):
    type: TypeEvent = TypeEvent.chat_participant_deleted
    chat_participant: ChatParticipantDelete


class UserStartTypingEvent(BaseEvent):
    type: TypeEvent = TypeEvent.user_start_typing
    user_id: int
    chat_id: int


class UserStopTypingEvent(BaseEvent):
    type: TypeEvent = TypeEvent.user_stop_typing
    user_id: int
    chat_id: int


class UserOnlineEvent(BaseEvent):
    type: TypeEvent = TypeEvent.user_online
    user: UserGet


class UserOfflineEvent(BaseEvent):
    type: TypeEvent = TypeEvent.user_offline
    user: UserGet
