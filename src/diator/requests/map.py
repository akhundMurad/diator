from typing import Type

from diator.requests.request import Request
from diator.requests.request_handler import RequestHandler


class RequestMap:
    def __init__(self) -> None:
        self._request_map: dict[Type[Request], Type[RequestHandler]] = {}

    def bind(
        self,
        request_type: Type[Request],
        handler_type: Type[RequestHandler],
    ) -> None:
        self._request_map[request_type] = handler_type

    def get(self, request_type: Type[Request]) -> Type[RequestHandler]:
        handler_type = self._request_map.get(request_type)
        if not handler_type:
            raise RequestHandlerDoesNotExist("RequestHandler not found matching Request type.")

        return handler_type

    def __str__(self) -> str:
        return str(self._request_map)


class RequestHandlerDoesNotExist(Exception):
    ...
