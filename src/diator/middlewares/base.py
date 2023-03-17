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


class BaseMiddleware:
    def __init__(self) -> None:
        self._request_handler: RequestHandler | None = None

    @property
    def request_handler(self) -> RequestHandler:
        if not self._request_handler:
            raise RuntimeError("RequestHandler is not set.")
        return self._request_handler

    @request_handler.setter
    def request_handler(self, request_handler: RequestHandler) -> None:
        self._request_handler = request_handler
