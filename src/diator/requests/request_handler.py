from typing import Protocol, TypeVar

from diator.mediator import Mediator
from diator.requests.request import Request
from diator.response import Response


Req_contra = TypeVar("Req_contra", bound=Request, contravariant=True)
Res_co = TypeVar("Res_co", Response, None, covariant=True)


class RequestHandler(Protocol[Req_contra, Res_co]):
    @property
    def mediator(self) -> Mediator:
        ...

    @mediator.setter
    def mediator(self, mediator: Mediator) -> None:
        ...

    async def handle(self, request: Req_contra) -> Res_co:
        ...
