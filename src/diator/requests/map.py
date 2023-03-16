from typing import Type, TypeVar

from diator.requests.request import Request
from diator.requests.request_handler import RequestHandler
from diator.response import Response


class RequestMap:
    def __init__(self) -> None:
        self._request_map: dict[Type[Request], Type[RequestHandler]] = {}

    def bind(
        self,
        request_type: Type[Request],
        handler_type: Type[RequestHandler[Request, Response]],
    ) -> None:
        self._request_map[request_type] = handler_type

    def get(self, request_type: Type[Request]) -> Type[RequestHandler[Request, Response]]:
        handler_type = self._request_map.get(request_type)
        if not handler_type:
            raise RequestHandlerDoesNotExist(
                "RequestHandler not found matching Request type."
            )

        return handler_type


class RequestHandlerDoesNotExist(Exception):
    ...
