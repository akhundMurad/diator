from dataclasses import dataclass, field
from uuid import UUID, uuid4

from diator.events.event import Event
from diator.events.event_emitter import EventEmitter
from diator.events.map import EventMap
from diator.events.message_brokers.protocol import Message
from diator.mediator import Mediator
from diator.requests.map import RequestMap
from diator.requests.request import Request
from diator.requests.request_handler import RequestHandler
from diator.response import Response


class FakeMessageBroker:
    async def send_message(self, message: Message) -> None:
        ...


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


class TestContainer:
    _handler = CloseMeetingRoomCommandHandler()

    def get(self, instance_type):
        return self._handler


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

    async def handle(
        self, request: ReadMeetingDetailsQuery
    ) -> ReadMeetingDetailsQueryResult:
        self.called = True
        return ReadMeetingDetailsQueryResult(meeting_room_id=request.meeting_room_id)


class TestQueryContainer:
    _handler = ReadMeetingDetailsQueryHandler()

    def get(self, instance_type):
        return self._handler


async def test_sending_request_with_response() -> None:
    event_emitter = EventEmitter(
        message_broker=FakeMessageBroker(),
        event_map=EventMap(),
        container=TestContainer(),
    )
    request_map = RequestMap()
    request_map.bind(ReadMeetingDetailsQuery, ReadMeetingDetailsQueryHandler)
    mediator = Mediator(
        request_map=request_map,
        container=TestQueryContainer(),
        event_emitter=event_emitter,
    )

    handler = TestQueryContainer().get(ReadMeetingDetailsQuery)

    assert not handler.called

    response = await mediator.send(ReadMeetingDetailsQuery(meeting_room_id=uuid4()))

    assert handler.called
    assert response
    assert isinstance(response, ReadMeetingDetailsQueryResult)
    assert response.meeting_room_id


async def test_sending_request_without_response() -> None:
    event_emitter = EventEmitter(
        message_broker=FakeMessageBroker(),
        event_map=EventMap(),
        container=TestContainer(),
    )
    request_map = RequestMap()
    request_map.bind(CloseMeetingRoomCommand, CloseMeetingRoomCommandHandler)
    mediator = Mediator(
        request_map=request_map, container=TestContainer(), event_emitter=event_emitter
    )

    handler = TestContainer().get(CloseMeetingRoomCommandHandler)

    assert not handler.called

    await mediator.send(CloseMeetingRoomCommand(meeting_room_id=uuid4()))

    assert handler.called
