from typing import Annotated, Type, Union

from pydantic import Field

from .events import (
    BaseEvent,
    ChatCreatedEvent,
    ChatCreateEvent,
    ChatDeletedEvent,
    ChatDeleteEvent,
    ChatParticipantCreatedEvent,
    ChatParticipantCreateEvent,
    ChatParticipantDeletedEvent,
    ChatParticipantDeleteEvent,
    ChatParticipantUpdatedEvent,
    ChatParticipantUpdateEvent,
    ChatUpdatedEvent,
    ChatUpdateEvent,
    MessageCreatedEvent,
    MessageCreateEvent,
    MessageDeletedEvent,
    MessageDeleteEvent,
    MessageUpdatedEvent,
    MessageUpdateEvent,
    TypeEvent,
    UserOfflineEvent,
    UserOnlineEvent,
    UserStartTypingEvent,
    UserStopTypingEvent,
)

EVENT_CLASSES_BY_TYPE: dict[TypeEvent, Type[BaseEvent]] = {
    TypeEvent.message_create: MessageCreateEvent,
    TypeEvent.message_created: MessageCreatedEvent,
    TypeEvent.message_update: MessageUpdateEvent,
    TypeEvent.message_updated: MessageUpdatedEvent,
    TypeEvent.message_delete: MessageDeleteEvent,
    TypeEvent.message_deleted: MessageDeletedEvent,
    TypeEvent.chat_create: ChatCreateEvent,
    TypeEvent.chat_created: ChatCreatedEvent,
    TypeEvent.chat_update: ChatUpdateEvent,
    TypeEvent.chat_updated: ChatUpdatedEvent,
    TypeEvent.chat_delete: ChatDeleteEvent,
    TypeEvent.chat_deleted: ChatDeletedEvent,
    TypeEvent.chat_participant_create: ChatParticipantCreateEvent,
    TypeEvent.chat_participant_created: ChatParticipantCreatedEvent,
    TypeEvent.chat_participant_update: ChatParticipantUpdateEvent,
    TypeEvent.chat_participant_updated: ChatParticipantUpdatedEvent,
    TypeEvent.chat_participant_delete: ChatParticipantDeleteEvent,
    TypeEvent.chat_participant_deleted: ChatParticipantDeletedEvent,
    TypeEvent.user_start_typing: UserStartTypingEvent,
    TypeEvent.user_stop_typing: UserStopTypingEvent,
    TypeEvent.user_online: UserOnlineEvent,
    TypeEvent.user_offline: UserOfflineEvent,
}


def parse_event(data: dict) -> BaseEvent:
    envelope = BaseEvent.model_validate(data)
    cls = EVENT_CLASSES_BY_TYPE[envelope.type]
    return cls.model_validate(data)


Event = Annotated[
    Union[
        MessageCreateEvent,
        MessageCreatedEvent,
        MessageUpdateEvent,
        MessageUpdatedEvent,
        MessageDeleteEvent,
        MessageDeletedEvent,
        ChatCreateEvent,
        ChatCreatedEvent,
        ChatUpdateEvent,
        ChatUpdatedEvent,
        ChatDeleteEvent,
        ChatDeletedEvent,
        ChatParticipantCreateEvent,
        ChatParticipantCreatedEvent,
        ChatParticipantUpdateEvent,
        ChatParticipantUpdatedEvent,
        ChatParticipantDeleteEvent,
        ChatParticipantDeletedEvent,
        UserStartTypingEvent,
        UserStopTypingEvent,
        UserOnlineEvent,
        UserOfflineEvent,
    ],
    Field(discriminator="type"),
]
