import logging

from backend.services.core.services_container import ServicesContainer
from backend.services.schemas.chat import ChatGet
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
    ChatParticipantUpdateEvent,
    ChatParticipantUpdatedEvent,
    TypeEvent,
)

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class ChatParticipantCreateHandler:
    async def handle(
        self,
        event: ChatParticipantCreateEvent,
        services: ServicesContainer,
        user_id: int,
    ) -> ChatParticipantCreatedEvent:

        participant_data = ChatParticipantPost.model_validate(event.chat_participant)

        participant_orm = await services.chat_participant_service.create_participant(
            chat_participant_data=participant_data
        )

        participant = ChatParticipantGet.model_validate(participant_orm)

        chat_orm = await services.chat_service.get_chat_by_id(chat_id=participant.chat_id)
        chat = ChatGet.model_validate(chat_orm)

        return ChatParticipantCreatedEvent(
            type=TypeEvent.chat_participant_created,
            chat_participant=participant,
            chat=chat,
        )


class ChatParticipantUpdateHandler:
    async def handle(
        self,
        event: ChatParticipantUpdateEvent,
        services: ServicesContainer,
        user_id: int,
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
        user_id: int,
    ) -> ChatParticipantDeletedEvent:

        chat_participant_id = event.chat_participant.id
        chat_id = event.chat_participant.chat_id
        user_id = event.chat_participant.user_id

        await services.chat_participant_service.delete_participant(
            chat_participant_id=chat_participant_id
        )

        logger.info(f'PARTICIPANT {user_id} WAS DELETED FROM CHAT {chat_id}')

        participant_deleted = ChatParticipantDelete(
            id=chat_participant_id, chat_id=chat_id, user_id=user_id
        )

        return ChatParticipantDeletedEvent(
            type=TypeEvent.chat_participant_deleted,
            chat_participant=participant_deleted,
        )
