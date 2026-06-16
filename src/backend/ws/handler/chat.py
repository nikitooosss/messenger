from backend.services.core.services_container import ServicesContainer
from backend.services.schemas.chat import (
    ChatDelete,
    ChatDetails,
    ChatGet,
    ChatPatch,
    ChatPost,
)
from backend.services.schemas.chat_participant import (
    ChatParticipantGet,
    ChatParticipantPost,
)

from ..schemas.events import (
    ChatCreatedEvent,
    ChatCreateEvent,
    ChatDeletedEvent,
    ChatDeleteEvent,
    ChatUpdatedEvent,
    ChatUpdateEvent,
    TypeEvent,
)


class ChatCreateHandler:
    async def handle(
        self,
        event: ChatCreateEvent,
        services: ServicesContainer,
        user_id: int,
    ):
        chat_orm = await services.chat_service.create_chat(
            chat_data=ChatPost(
                name=event.chat.name,
                is_group=event.chat.is_group,
            )
        )

        participants_data = [
            ChatParticipantPost(
                chat_id=chat_orm.id,
                user_id=participant.user_id,
                role=participant.role,
            )
            for participant in event.participants
        ]

        participants_orm = [
            await services.chat_participant_service.create_participant(p)
            for p in participants_data
        ]

        participants = [ChatParticipantGet.model_validate(p) for p in participants_orm]

        chat = ChatDetails(
            id=chat_orm.id,
            name=chat_orm.name,
            is_group=chat_orm.is_group,
            created_at=chat_orm.created_at,
            participants=participants,
        )
        return ChatCreatedEvent(
            type=TypeEvent.chat_created,
            chat=chat,
            participants=participants,
        )


class ChatUpdateHandler:
    async def handle(
        self,
        event: ChatUpdateEvent,
        services: ServicesContainer,
        user_id: int,
    ):
        chat_id = event.chat.id
        chat_data = ChatPatch.model_validate(event.chat.model_dump(exclude_none=True))

        chat_orm = await services.chat_service.update_chat(
            chat_id=chat_id, chat_data=chat_data
        )
        chat = ChatGet.model_validate(chat_orm)

        return ChatUpdatedEvent(type=TypeEvent.chat_updated, chat=chat)


class ChatDeleteHandler:
    async def handle(
        self,
        event: ChatDeleteEvent,
        services: ServicesContainer,
        user_id: int,
    ):
        chat_id = event.chat.id

        participants_orm = (
            await services.chat_participant_service.get_all_chat_participants(
                chat_id=chat_id
            )
        )

        user_participant = next(
            (p for p in participants_orm if p.user_id == user_id), None
        )
        if user_participant is None or user_participant.role.value != "admin":
            raise PermissionError("Only admins can delete a chat")

        participants = [ChatParticipantGet.model_validate(p) for p in participants_orm]

        await services.chat_service.delete_chat(chat_id=chat_id)

        chat_deleted = ChatDelete(id=chat_id)

        return ChatDeletedEvent(
            type=TypeEvent.chat_deleted,
            chat=chat_deleted,
            participants=participants,
        )
