from typing import Type

from diator.container.protocol import Container
from diator.events import Event, EventEmitter
from diator.middlewares import MiddlewareChain
from diator.requests import RequestMap, Request
from diator.response import Response
from diator.dispatcher import Dispatcher, DefaultDispatcher


class Mediator:
    """
    The main mediator object.

    Usage::

      redis_client = Redis()  # async redis client
      message_broker = RedisMessageBroker(redis_client)
      event_map =  EventMap()
      event_map.bind(UserJoinedDomainEvent, UserJoinedDomainEventHandler)
      request_map = RequestMap()
      request_map.bind(JoinUserCommand, JoinUserCommandHandler)
      event_emitter = EventEmitter(message_broker, event_emitter, container)

      mediator = Mediator(request_map, event_emitter, container)

      # Handles command and published events by the command handler.
      await mediator.send(join_user_command)

    """

    def __init__(
        self,
        request_map: RequestMap,
        event_emitter: EventEmitter,
        container: Container,
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
        while events:
            event = events.pop()
            await self._event_emitter.emit(event)
