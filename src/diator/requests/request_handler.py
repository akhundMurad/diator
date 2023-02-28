from typing import Protocol, TypeVar

from diator.events.event import Event
from diator.requests.request import Request
from diator.response import Response


Req = TypeVar("Req", bound=Request, contravariant=True)
Res = TypeVar("Res", Response, None, covariant=True)


class RequestHandler(Protocol[Req, Res]):
    @property
    def events(self) -> list[Event]:
        ...

    def add_event(self, event: Event) -> None:
        ...

    async def handle(self, request: Req) -> Res:
        raise NotImplementedError
