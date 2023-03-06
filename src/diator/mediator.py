from typing import Type

from diator.container import Container
from diator.events.event import Event
from diator.events.event_emitter import EventEmitter
from diator.requests.map import RequestMap
from diator.requests.request import Request
from diator.requests.request_handler import RequestHandler
from diator.response import Response


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
    ) -> None:
        self._request_map = request_map
        self._container = container
        self._event_emitter = event_emitter

    async def send(self, request: Request) -> Response | None:
        handler_type = self._request_map.get(type(request))
        handler = self._container.get(handler_type)

        response = await handler.handle(request)

        if handler.events:
            await self._send_events(handler.events.copy())

        return response

    def bind_request_handler(
        self, request_type: Type[Request], handler_type: Type[RequestHandler]
    ) -> None:
        self._request_map.bind(request_type=request_type, handler_type=handler_type)

    async def _send_events(self, events: list[Event]) -> None:
        while events:
            event = events.pop()
            await self._event_emitter.emit(event)
