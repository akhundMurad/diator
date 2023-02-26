from diator.container import Container
from diator.requests.request import Request
from diator.response import Response
from diator.map import RequestMap


class Mediator:
    def __init__(
        self,
        request_map: RequestMap,
        container: Container,
    ) -> None:
        self._request_map = request_map
        self._container = container

    async def send(self, request: Request) -> Response | None:
        handler_type = self._request_map.get(type(request))

        handler = self._container.get(handler_type)
        handler.mediator = self

        response = await handler.handle(request)

        return response
