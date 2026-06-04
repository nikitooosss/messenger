from backend.services.core.services_container import ServicesContainer
from backend.services.schemas.message import (
    MessageDelete,
    MessageGet,
    MessagePatch,
    MessagePost,
)

from ..schemas.events import (
    MessageCreatedEvent,
    MessageCreateEvent,
    MessageDeletedEvent,
    MessageDeleteEvent,
    MessageUpdatedEvent,
    MessageUpdateEvent,
    TypeEvent,
)


class MessageCreateHandler:
    async def handle(
        self,
        event: MessageCreateEvent,
        services: ServicesContainer,
    ):
        chat_id = event.message.chat_id
        user_id = event.message.user_id
        content = event.message.content

        message_data = MessagePost(chat_id=chat_id, user_id=user_id, content=content)

        message_orm = await services.message_service.create_message(
            message_data=message_data
        )
        message = MessageGet.model_validate(message_orm)

        return MessageCreatedEvent(type=TypeEvent.message_created, message=message)


class MessageUpdateHandler:
    async def handle(
        self,
        event: MessageUpdateEvent,
        services: ServicesContainer,
    ):
        message_id = event.message.id
        message_data = MessagePatch.model_validate(
            event.message.model_dump(exclude_none=True)
        )

        message_orm = await services.message_service.update_message(
            message_id=message_id, message_data=message_data
        )

        message = MessageGet.model_validate(message_orm)

        return MessageUpdatedEvent(type=TypeEvent.message_updated, message=message)


class MessageDeleteHandler:
    async def handle(
        self,
        event: MessageDeleteEvent,
        services: ServicesContainer,
    ):
        message_id = event.message.id

        await services.message_service.delete_message(message_id=message_id)

        message_deleted = MessageDelete(id=message_id)

        return MessageDeletedEvent(
            type=TypeEvent.message_deleted, message=message_deleted
        )
