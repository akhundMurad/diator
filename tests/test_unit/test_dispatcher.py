from dataclasses import dataclass, field
from uuid import UUID, uuid4
from diator.events import Event
from diator.middlewares import BaseMiddleware
from diator.requests.map import RequestMap
from diator.requests import Request, RequestHandler
from diator.response import Response
from diator.dispatcher import DefaultDispatcher


@dataclass(kw_only=True)
class ReadMeetingDetailsQuery:
    meeting_room_id: UUID = field()


@dataclass(kw_only=True)
class ReadMeetingDetailsQueryResult:
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


async def test_default_dispatcher_logic() -> None:
    middleware = FirstMiddleware()
    request_map = RequestMap()
    request_map.bind(ReadMeetingDetailsQuery, ReadMeetingDetailsQueryHandler)
    dispatcher = DefaultDispatcher(
        request_map=request_map,
        container=TestQueryContainer(),
        middlewares=[middleware],
    )

    request = ReadMeetingDetailsQuery(meeting_room_id=uuid4())

    result = await dispatcher.dispatch(request)

    assert request.meeting_room_id == "REQ"
    assert result.response.meeting_room_id == "RES"


async def test_default_dispatcher_chain_logic() -> None:
    request_map = RequestMap()
    request_map.bind(ReadMeetingDetailsQuery, ReadMeetingDetailsQueryHandler)
    dispatcher = DefaultDispatcher(
        request_map=request_map,
        container=TestQueryContainer(),
        middlewares=[FirstMiddleware(), SecondMiddleware(), ThirdMiddleware()],
    )

    request = ReadMeetingDetailsQuery(meeting_room_id=uuid4())

    result = await dispatcher.dispatch(request)

    assert request.meeting_room_id == "REQ"
    assert result.response.meeting_room_id == "RES"

    assert request.second == "DONE"
    assert result.response.second == "DONE"

    assert request.third == "DONE"
    assert result.response.third == "DONE"


class FirstMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def process_request(self, request: Request) -> None:
        request.meeting_room_id = "REQ"

    async def process_response(self, response: Response) -> None:
        response.meeting_room_id = "RES"


class SecondMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def process_request(self, request: Request) -> None:
        request.second = "DONE"

    async def process_response(self, response: Response) -> None:
        response.second = "DONE"


class ThirdMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def process_request(self, request: Request) -> None:
        request.third = "DONE"

    async def process_response(self, response: Response) -> None:
        response.third = "DONE"
