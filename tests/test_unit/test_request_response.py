from dataclasses import dataclass, field
from uuid import UUID, uuid4

from diator.events import Event, EventEmitter, EventMap
from diator.events.message_brokers.redis import Message
from diator.mediator import Mediator
from diator.requests import Request, RequestHandler, RequestMap
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

    async def resolve(self, type_):
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

    async def resolve(self, type_):
        return self._handler


async def test_sending_request_with_response() -> None:
    event_emitter = EventEmitter(
        message_broker=FakeMessageBroker(),
        event_map=EventMap(),
        container=TestContainer(),  # type: ignore
    )
    request_map = RequestMap()
    request_map.bind(ReadMeetingDetailsQuery, ReadMeetingDetailsQueryHandler)
    mediator = Mediator(
        request_map=request_map,
        container=TestQueryContainer(),  # type: ignore
        event_emitter=event_emitter,
    )

    handler = await TestQueryContainer().resolve(ReadMeetingDetailsQuery)

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
        container=TestContainer(),  # type: ignore
    )
    request_map = RequestMap()
    request_map.bind(CloseMeetingRoomCommand, CloseMeetingRoomCommandHandler)
    mediator = Mediator(
        request_map=request_map, container=TestContainer(), event_emitter=event_emitter  # type: ignore
    )

    handler = await TestContainer().resolve(CloseMeetingRoomCommandHandler)

    assert not handler.called

    await mediator.send(CloseMeetingRoomCommand(meeting_room_id=uuid4()))

    assert handler.called
