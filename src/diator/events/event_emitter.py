import logging
from functools import singledispatchmethod

from dataclass_factory import Factory

from diator.container import Container
from diator.events.event import DomainEvent, ECSTEvent, Event, NotificationEvent
from diator.events.map import EventMap
from diator.events.message_brokers.protocol import Message, MessageBroker

logger = logging.getLogger(__name__)


class EventEmitter:
    """
    The event emitter is responsible for sending events to the according handlers or
    to the message broker abstraction.

    Usage::

      redis_client = Redis()  # async redis client
      message_broker = RedisMessageBroker(redis_client)
      event_map =  EventMap()
      event_map.bind(UserJoinedDomainEvent, UserJoinedDomainEventHandler)

      event_emitter = EventEmitter(message_broker, event_emitter, container)

      # Uses UserJoinedDomainEventHandler for handling event:
      await event_emitter.emit(user_joined_domain_event)

      # Sends event to the Redis Pub/Sub:
      await event_emitter.emit(user_joined_notification_event)

    """

    def __init__(
        self, message_broker: MessageBroker, event_map: EventMap, container: Container
    ) -> None:
        self._message_broker = message_broker
        self._event_map = event_map
        self._container = container

    @singledispatchmethod
    async def emit(self, event: Event) -> None:
        ...

    @emit.register
    async def _(self, event: DomainEvent) -> None:
        handlers_types = self._event_map.get(type(event))

        for handler_type in handlers_types:
            handler = self._container.get(handler_type)
            logger.info(
                "Handling Event(%s) via event handler(%s)",
                type(event).__name__,
                handler_type.__name__,
            )
            await handler.handle(event)

    @emit.register
    async def _(self, event: NotificationEvent) -> None:
        message = _build_message(event)

        logger.info(
            "Sending Notification Event(%s) to message broker %s",
            event.event_id,
            type(self._message_broker).__name__,
        )

        await self._message_broker.send_message(message)

    @emit.register
    async def _(self, event: ECSTEvent) -> None:
        message = _build_message(event)

        logger.info(
            "Sending ECST event(%s) to message broker %s",
            event.event_id,
            type(self._message_broker).__name__,
        )

        await self._message_broker.send_message(message)


def _build_message(event: NotificationEvent | ECSTEvent) -> Message:
    factory = Factory()

    payload = factory.dump(event)

    return Message(
        message_type=event._event_type,
        message_name=type(event).__name__,
        message_id=event.event_id,
        payload=payload,
    )
