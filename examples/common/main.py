import asyncio
from redis import asyncio as redis
from rodi import Container

from examples.common.join_meeting_room_command import JoinMeetingRoomCommand
from examples.common.join_meeting_room_command_handler import (
    JoinMeetingRoomCommandHandler,
)
from examples.common.user_joined_domain_event import UserJoinedDomainEvent
from examples.common.user_joined_event_handler import UserJoinedEventHandler

from diator.requests import RequestMap
from diator.events.message_brokers import RedisMessageBroker
from diator.events import EventEmitter
from diator.mediator import Mediator
from diator.events import EventMap
from diator.container import RodiContainer


def configure_di() -> RodiContainer:
    container = Container()

    container.register(UserJoinedEventHandler)
    container.register(JoinMeetingRoomCommandHandler)

    rodi_container = RodiContainer()
    rodi_container.attach_external_container(container)

    return rodi_container


async def main() -> None:
    event_map = EventMap()
    event_map.bind(UserJoinedDomainEvent, UserJoinedEventHandler)
    request_map = RequestMap()
    request_map.bind(JoinMeetingRoomCommand, JoinMeetingRoomCommandHandler)
    container = configure_di()

    redis_client = redis.Redis.from_url("redis://localhost:6379/0")

    event_emitter = EventEmitter(
        message_broker=RedisMessageBroker(redis_client),
        event_map=event_map,
        container=container,
    )

    mediator = Mediator(
        request_map=request_map, event_emitter=event_emitter, container=container
    )

    await mediator.send(JoinMeetingRoomCommand(user_id=1))


if __name__ == "__main__":
    asyncio.run(main())
