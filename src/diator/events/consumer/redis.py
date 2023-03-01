import logging
from typing import Type
import orjson
from redis import asyncio as redis
from dataclass_factory import Factory

from diator.container import Container
from diator.events.event import Event
from diator.events.event_handler import EventHandler
from diator.generics import E_contra
from diator.events.map import EventMap


logger = logging.getLogger(__name__)


class RedisConsumer:
    def __init__(
        self,
        event_map: EventMap,
        container: Container,
        redis_client: redis.Redis,
        *,
        channel_prefix: str | None = None,
    ) -> None:
        self._event_map = event_map
        self._container = container
        self._redis_client = redis_client
        self._channel_prefix = channel_prefix or "python_diator_channel"

    async def consume(self) -> None:
        async with self._redis_client.pubsub() as pubsub:
            logger.info(
                "Redis Consumer has been started on %s channel", self._channel_prefix
            )

            await pubsub.psubscribe(f"{self._channel_prefix}:*")

            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if not message:
                    continue

                event = self._build_event_from_message(message)

                handlers_types = self._event_map.get(type(event))

                for handler_type in handlers_types:
                    handler = self._container.get(handler_type)
                    logger.debug(
                        "Handling event(%s) via handler(%s).",
                        type(event).__name__,
                        type(handler_type).__name__,
                    )
                    await handler.handle(event)

    def bind_event_handler(
        self, event_type: Type[E_contra], event_handler: Type[EventHandler[E_contra]]
    ) -> None:
        self._event_map.bind(event_type=event_type, handler_type=event_handler)

    def _get_event_by_name(self, event_name: str) -> Type[Event]:
        events = self._event_map.get_events()
        event = list(
            filter(lambda event_type: event_type.__name__ == event_name, events)
        )
        if not event:
            raise EventNotFound(f"Event with name {event_name} was not found.")

        return event[0]

    def _build_event_from_message(self, message: dict) -> Event:
        data: dict = orjson.loads(message["data"].decode())
        channel: str = message["channel"].decode()
        event_name = channel.split(":")[-1]

        event_type = self._get_event_by_name(event_name)
        logger.debug("Event(%s) has been handled from message broker.", event_name)
        dataclass_factory = Factory()
        return dataclass_factory.load(data, event_type)


class EventNotFound(Exception):
    ...
