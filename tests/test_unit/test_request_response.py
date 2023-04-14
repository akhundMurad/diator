from dataclasses import dataclass, field
from typing import Type
from uuid import UUID, uuid4

import pytest

from diator.events import Event, EventEmitter, EventMap
from diator.mediator import Mediator
from diator.requests import Request, RequestHandler, RequestMap
from diator.response import Response


@dataclass(frozen=True, kw_only=True)
class CloseMeetingRoomCommand(Request):
    meeting_room_id: UUID = field()


class CloseMeetingRoomCommandHandler(RequestHandler[CloseMeetingRoomCommand, None]):
    def __init__(self) -> None:
        self.called = False
        self._events: list[Event] = []

    @property
    def events(self) -> list:
        return self._events

    async def handle(self, request: CloseMeetingRoomCommand) -> None:
        self.called = True


@dataclass(frozen=True, kw_only=True)
class ReadMeetingDetailsQuery(Request):
    meeting_room_id: UUID = field()


@dataclass(frozen=True, kw_only=True)
class ReadMeetingDetailsQueryResult(Response):
    meeting_room_id: UUID = field()


class ReadMeetingDetailsQueryHandler(
    RequestHandler[ReadMeetingDetailsQuery, ReadMeetingDetailsQueryResult]  # type: ignore
):
    def __init__(self) -> None:
        self.called = False
        self._events: list[Event] = []

    @property
    def events(self) -> list:
        return self._events

    async def handle(self, request: ReadMeetingDetailsQuery) -> ReadMeetingDetailsQueryResult:
        self.called = True
        return ReadMeetingDetailsQueryResult(meeting_room_id=request.meeting_room_id)


class TestContainer:
    command_handler = CloseMeetingRoomCommandHandler()
    query_handler = ReadMeetingDetailsQueryHandler()

    async def resolve(self, type_: Type):
        if isinstance(self.command_handler, type_):
            return self.command_handler
        elif isinstance(self.query_handler, type_):
            return self.query_handler


@pytest.fixture
def mediator() -> Mediator:
    event_emitter = EventEmitter(
        event_map=EventMap(),
        container=TestContainer(),  # type: ignore
    )
    request_map = RequestMap()
    request_map.bind(ReadMeetingDetailsQuery, ReadMeetingDetailsQueryHandler)
    request_map.bind(CloseMeetingRoomCommand, CloseMeetingRoomCommandHandler)
    return Mediator(
        request_map=request_map,
        container=TestContainer(),  # type: ignore
        event_emitter=event_emitter,
    )


async def test_sending_request_with_response(mediator: Mediator) -> None:
    handler = await TestContainer().resolve(ReadMeetingDetailsQueryHandler)

    assert not handler.called

    response = await mediator.send(ReadMeetingDetailsQuery(meeting_room_id=uuid4()))

    assert handler.called
    assert response
    assert isinstance(response, ReadMeetingDetailsQueryResult)
    assert response.meeting_room_id


async def test_sending_request_without_response(mediator: Mediator) -> None:
    handler = await TestContainer().resolve(CloseMeetingRoomCommandHandler)
    assert not handler.called

    await mediator.send(CloseMeetingRoomCommand(meeting_room_id=uuid4()))

    assert handler.called
