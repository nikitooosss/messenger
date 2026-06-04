import pytest

from backend.ws.router import EventRouter
from backend.ws.schemas.events import BaseEvent, TypeEvent


def test_route_unknown_event_raises_error():
    router = EventRouter()
    event = BaseEvent(type=TypeEvent.chat_create)

    with pytest.raises(ValueError, match="Unknown event type"):
        router.route(event=event, ws_manager=None)
