from typing import Sequence

from diator.container.protocol import Container
from diator.dispatcher.dispatch_result import DispatchResult
from diator.requests.map import RequestMap
from diator.requests.request import Request
from diator.middlewares.base import Middleware
from diator.requests.request_handler import RequestHandler
from diator.response import Response


class DefaultDispatcher:
    def __init__(
        self,
        request_map: RequestMap,
        container: Container,
        middlewares: Sequence[Middleware] | None = None,
    ) -> None:
        self._request_map = request_map
        self._container = container
        self._middlewares = middlewares or ()

    async def dispatch(self, request: Request) -> DispatchResult:
        handler_type = self._request_map.get(type(request))
        handler = await self._container.resolve(handler_type)

        await self._iter_request_middleware_stack(handler, request)

        response = await handler.handle(request)

        if response:
            await self._iter_response_middleware_stack(handler, response)

        return DispatchResult(response=response, events=handler.events)

    async def _iter_request_middleware_stack(
        self, handler: RequestHandler, request: Request
    ) -> None:
        for middleware in self._middlewares:
            middleware.request_handler = handler
            await middleware.process_request(request)

    async def _iter_response_middleware_stack(
        self, handler: RequestHandler, response: Response
    ) -> None:
        for middleware in self._middlewares:
            middleware.request_handler = handler
            await middleware.process_response(response)
