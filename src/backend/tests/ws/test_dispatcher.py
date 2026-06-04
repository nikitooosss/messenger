import pytest

from backend.ws.dispatcher import WSDispatcher
from backend.ws.schemas.events import BaseEvent, TypeEvent


@pytest.mark.asyncio
async def test_dispatch_unknown_event_raises_error():
    dispatcher = WSDispatcher()
    event = BaseEvent(type=TypeEvent.user_online)

    with pytest.raises(ValueError, match="Unknown event type"):
        await dispatcher.dispatch(event=event, services=None)
