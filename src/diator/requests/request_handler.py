from typing import Protocol, TypeVar

from diator.events.event import Event
from diator.requests.request import Request
from diator.response import Response

Req = TypeVar("Req", bound=Request, contravariant=True)
Res = TypeVar("Res", Response, None, covariant=True)


class RequestHandler(Protocol[Req, Res]):
    """
    The request handler interface.

    The request handler is an object, which gets a request as input and may return a response as a result.

    Command handler example::

      class JoinMeetingCommandHandler(RequestHandler[JoinMeetingCommand, None])
          def __init__(self, meetings_api: MeetingAPIProtocol) -> None:
              self._meetings_api = meetings_api
              self.events: list[Event] = []

          async def handle(self, request: JoinMeetingCommand) -> None:
              await self._meetings_api.join_user(request.user_id, request.meeting_id)

    Query handler example::

      class ReadMeetingQueryHandler(RequestHandler[ReadMeetingQuery, ReadMeetingQueryResult])
          def __init__(self, meetings_api: MeetingAPIProtocol) -> None:
              self._meetings_api = meetings_api
              self.events: list[Event] = []

          async def handle(self, request: ReadMeetingQuery) -> ReadMeetingQueryResult:
              link = await self._meetings_api.get_link(request.meeting_id)
              return ReadMeetingQueryResult(link=link, meeting_id=request.meeting_id)

    """

    @property
    def events(self) -> list[Event]:
        ...

    async def handle(self, request: Req) -> Res:
        raise NotImplementedError
