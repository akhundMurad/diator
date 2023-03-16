from typing import Protocol
from diator.requests.request import Request

from diator.requests.request_handler import RequestHandler
from diator.response import Response


class Middleware(Protocol):
    @property
    def request_handler(self) -> RequestHandler:
        ...

    @request_handler.setter
    def request_handler(self, request_handler: RequestHandler) -> None:
        ...

    async def process_request(self, request: Request) -> None:
        ...

    async def process_response(self, response: Response) -> None:
        ...
