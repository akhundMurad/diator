import asyncio
import os
from datetime import timedelta

import rodi
from azure.servicebus.aio import ServiceBusClient

from diator.container.rodi import RodiContainer
from diator.events.event_emitter import EventEmitter
from diator.events.map import EventMap
from diator.mediator import Mediator
from diator.message_brokers.azure import AzureMessageBroker
from diator.requests import RequestMap

from .command import CleanUnactiveUsersCommand
from .command_handler import CleanUnactiveUsersCommandHandler


def configure_di() -> RodiContainer:
    external_container = rodi.Container()
    external_container.register(CleanUnactiveUsersCommandHandler)

    container = RodiContainer()
    container.attach_external_container(external_container)
    return container


async def main() -> None:
    container = configure_di()
    request_map = RequestMap()
    request_map.bind(CleanUnactiveUsersCommand, CleanUnactiveUsersCommandHandler)

    azure_service_bus_client = ServiceBusClient.from_connection_string(os.getenv("CONNECTION_STRING"))
    message_broker = AzureMessageBroker(azure_service_bus_client, os.getenv("TOPIC_NAME"), timeout=15)
    event_emitter = EventEmitter(message_broker=message_broker, event_map=EventMap(), container=container)

    mediator = Mediator(event_emitter=event_emitter, request_map=request_map, container=container)

    await mediator.send(CleanUnactiveUsersCommand(eta=timedelta(days=1)))


if __name__ == "__main__":
    asyncio.run(main())
