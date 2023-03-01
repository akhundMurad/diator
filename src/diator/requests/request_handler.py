from typing import Protocol

from diator.events.event import Event
from diator.generics import Req_contra, Res_co


class RequestHandler(Protocol[Req_contra, Res_co]):
    @property
    def events(self) -> list[Event]:
        ...

    async def handle(self, request: Req_contra) -> Res_co:
        raise NotImplementedError
