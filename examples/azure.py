import asyncio
import os
from dataclasses import dataclass
from datetime import timedelta

import rodi
from azure.servicebus.aio import ServiceBusClient

from diator.container.rodi import RodiContainer
from diator.events import EventEmitter, EventMap, NotificationEvent
from diator.mediator import Mediator
from diator.message_brokers.azure import AzureMessageBroker
from diator.requests import Request, RequestHandler, RequestMap


@dataclass(frozen=True, kw_only=True)
class CleanUnactiveUsersCommand(Request):
    eta: timedelta


@dataclass(frozen=True, kw_only=True)
class UnactiveUsersCleaned(NotificationEvent):
    ids: list


class CleanUnactiveUsersCommandHandler(RequestHandler[CleanUnactiveUsersCommand, None]):
    def __init__(self) -> None:
        self._events = []

    @property
    def events(self) -> list:
        return self._events

    async def handle(self, request: CleanUnactiveUsersCommand) -> None:
        self._events.append(UnactiveUsersCleaned(ids=[1, 2, 3, 4, 5]))


def configure_di() -> RodiContainer:
    external_container = rodi.Container()
    external_container.register(CleanUnactiveUsersCommandHandler)

    container = RodiContainer()
    container.attach_external_container(external_container)
    return container


async def main() -> None:
    service_bus_connection_string = os.getenv("CONNECTION_STRING")
    topic_name = os.getenv("TOPIC_NAME")

    container = configure_di()
    request_map = RequestMap()
    request_map.bind(CleanUnactiveUsersCommand, CleanUnactiveUsersCommandHandler)

    azure_service_bus_client = ServiceBusClient.from_connection_string(service_bus_connection_string)
    message_broker = AzureMessageBroker(azure_service_bus_client, topic_name, timeout=15)
    event_emitter = EventEmitter(message_broker=message_broker, event_map=EventMap(), container=container)

    mediator = Mediator(event_emitter=event_emitter, request_map=request_map, container=container)

    await mediator.send(CleanUnactiveUsersCommand(eta=timedelta(days=1)))


if __name__ == "__main__":
    asyncio.run(main())
