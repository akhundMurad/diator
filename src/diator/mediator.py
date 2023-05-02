from typing import Type

from diator.container.protocol import Container
from diator.dispatcher import DefaultDispatcher, Dispatcher
from diator.events import Event, EventEmitter
from diator.middlewares import MiddlewareChain
from diator.requests import Request, RequestMap
from diator.response import Response


class Mediator:
    """
    The main mediator object.

    Usage::

      redis_client = Redis()  # async redis client
      message_broker = RedisMessageBroker(redis_client)
      event_map = EventMap()
      event_map.bind(UserJoinedDomainEvent, UserJoinedDomainEventHandler)
      request_map = RequestMap()
      request_map.bind(JoinUserCommand, JoinUserCommandHandler)
      event_emitter = EventEmitter(event_map, container, message_broker)

      mediator = Mediator(
        event_emitter=event_emitter,
        request_map=request_map,
        container=container
      )

      # Handles command and published events by the command handler.
      await mediator.send(join_user_command)

    """

    def __init__(
        self,
        request_map: RequestMap,
        container: Container,
        event_emitter: EventEmitter | None = None,
        middleware_chain: MiddlewareChain | None = None,
        *,
        dispatcher_type: Type[Dispatcher] = DefaultDispatcher,
    ) -> None:
        self._event_emitter = event_emitter
        self._dispatcher = dispatcher_type(
            request_map=request_map, container=container, middleware_chain=middleware_chain  # type: ignore
        )

    async def send(self, request: Request) -> Response | None:
        dispatch_result = await self._dispatcher.dispatch(request)

        if dispatch_result.events:
            await self._send_events(dispatch_result.events.copy())

        return dispatch_result.response

    async def _send_events(self, events: list[Event]) -> None:
        if not self._event_emitter:
            return

        while events:
            event = events.pop()
            await self._event_emitter.emit(event)
