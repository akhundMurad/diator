from typing import Protocol

from diator.requests.request import Request
from diator.response import Response


class Middleware(Protocol):
    async def handle_request(self, request: Request) -> Request:
        ...

    async def handle_response(self, response: Response) -> Response:
        ...
