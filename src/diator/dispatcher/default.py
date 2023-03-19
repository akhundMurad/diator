from diator.container.protocol import Container
from diator.dispatcher.dispatch_result import DispatchResult
from diator.requests.request import Request
from diator.requests.map import RequestMap
from diator.middlewares.base import MiddlewareChain


class DefaultDispatcher:
    def __init__(
        self,
        request_map: RequestMap,
        container: Container,
        middleware_chain: MiddlewareChain | None = None,
    ) -> None:
        self._request_map = request_map
        self._container = container
        self._middleware_chain = middleware_chain or MiddlewareChain()

    async def dispatch(self, request: Request) -> DispatchResult:
        handler_type = self._request_map.get(type(request))
        handler = await self._container.resolve(handler_type)

        wrapped_handler = self._middleware_chain.wrap(handler)

        response = await wrapped_handler.handle(request)

        return DispatchResult(response=response, events=wrapped_handler.events)
