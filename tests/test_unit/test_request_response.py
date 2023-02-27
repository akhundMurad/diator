from dataclasses import dataclass, field
from uuid import UUID, uuid4

from diator.mediator import Mediator
from diator.requests.request import Request
from diator.requests.request_handler import RequestHandler
from diator.map import RequestMap
from diator.response import Response


@dataclass(frozen=True, slots=True)
class CloseMeetingRoomCommand(Request):
    meeting_room_id: UUID = field()


class CloseMeetingRoomCommandHandler(RequestHandler[CloseMeetingRoomCommand, None]):
    def __init__(self) -> None:
        self.called = False

    async def handle(self, request: CloseMeetingRoomCommand) -> None:
        self.called = True


class TestContainer:
    _handler = CloseMeetingRoomCommandHandler()

    def get(self, instance_type):
        return self._handler


async def test_sending_request_without_response() -> None:
    request_map = RequestMap()
    request_map.bind(CloseMeetingRoomCommand, CloseMeetingRoomCommandHandler)
    mediator = Mediator(request_map=request_map, container=TestContainer())

    handler = TestContainer().get(CloseMeetingRoomCommandHandler)

    assert not handler.called

    await mediator.send(CloseMeetingRoomCommand(meeting_room_id=uuid4()))

    assert handler.called


@dataclass(frozen=True, slots=True)
class ReadMeetingDetailsQuery(Request):
    meeting_room_id: UUID = field()


@dataclass(frozen=True, slots=True)
class ReadMeetingDetailsQueryResult(Response):
    meeting_room_id: UUID = field()


class ReadMeetingDetailsQueryHandler(
    RequestHandler[ReadMeetingDetailsQuery, ReadMeetingDetailsQueryResult]
):
    def __init__(self) -> None:
        self.called = False

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
    request_map = RequestMap()
    request_map.bind(ReadMeetingDetailsQuery, ReadMeetingDetailsQueryHandler)
    mediator = Mediator(request_map=request_map, container=TestQueryContainer())

    handler = TestQueryContainer().get(ReadMeetingDetailsQuery)

    assert not handler.called

    response = await mediator.send(ReadMeetingDetailsQuery(meeting_room_id=uuid4()))

    assert handler.called
    assert response
    assert isinstance(response, ReadMeetingDetailsQueryResult)
    assert response.meeting_room_id
