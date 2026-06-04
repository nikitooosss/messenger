from backend.services.core.services_container import ServicesContainer
from backend.services.schemas.chat_participant import (
    ChatParticipantDelete,
    ChatParticipantGet,
    ChatParticipantPatch,
    ChatParticipantPost,
)

from ..schemas.events import (
    ChatParticipantCreatedEvent,
    ChatParticipantCreateEvent,
    ChatParticipantDeletedEvent,
    ChatParticipantDeleteEvent,
    ChatParticipantUpdatedEvent,
    TypeEvent,
)


class ChatParticipantCreateHandler:
    async def handle(
        self,
        event: ChatParticipantCreateEvent,
        services: ServicesContainer,
    ) -> ChatParticipantCreatedEvent:

        participant_data = ChatParticipantPost.model_validate(event.chat_participant)

        participant_orm = await services.chat_participant_service.create_participant(
            chat_participant_data=participant_data
        )

        participant = ChatParticipantGet.model_validate(participant_orm)

        return ChatParticipantCreatedEvent(
            type=TypeEvent.chat_participant_created,
            chat_participant=participant,
        )


class ChatParticipantUpdateHandler:
    async def handle(
        self,
        event: ChatParticipantUpdatedEvent,
        services: ServicesContainer,
    ) -> ChatParticipantUpdatedEvent:

        patch_data = ChatParticipantPatch.model_validate(event.chat_participant)

        participant_orm = await services.chat_participant_service.update_participant(
            chat_participant_id=patch_data.id,
            chat_participant_data=patch_data,
        )

        participant = ChatParticipantGet.model_validate(participant_orm)

        return ChatParticipantUpdatedEvent(
            type=TypeEvent.chat_participant_updated,
            chat_participant=participant,
        )


class ChatParticipantDeleteHandler:
    async def handle(
        self,
        event: ChatParticipantDeleteEvent,
        services: ServicesContainer,
    ) -> ChatParticipantDeletedEvent:

        chat_participant_id = event.chat_participant.id
        chat_id = event.chat_participant.chat_id
        user_id = event.chat_participant.user_id

        await services.chat_participant_service.delete_participant(
            chat_participant_id=chat_participant_id
        )

        participant_deleted = ChatParticipantDelete(
            id=chat_participant_id, chat_id=chat_id, user_id=user_id
        )

        return ChatParticipantDeletedEvent(
            type=TypeEvent.chat_participant_deleted,
            chat_participant=participant_deleted,
        )
