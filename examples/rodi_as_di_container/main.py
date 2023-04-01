import asyncio

from redis import asyncio as redis
from rodi import Container

from diator.container.rodi import RodiContainer
from diator.events import EventEmitter, EventMap
from diator.mediator import Mediator
from diator.message_brokers.redis import RedisMessageBroker
from diator.middlewares import MiddlewareChain
from diator.requests import RequestMap

from .join_meeting_room_command import JoinMeetingRoomCommand
from .join_meeting_room_command_handler import JoinMeetingRoomCommandHandler
from .middlewares import FirstMiddleware, SecondMiddleware
from .user_joined_domain_event import UserJoinedDomainEvent
from .user_joined_event_handler import UserJoinedEventHandler


def configure_di() -> RodiContainer:
    container = Container()

    container.register(UserJoinedEventHandler)
    container.register(JoinMeetingRoomCommandHandler)

    rodi_container = RodiContainer()
    rodi_container.attach_external_container(container)

    return rodi_container


async def main() -> None:
    middleware_chain = MiddlewareChain()
    middleware_chain.add(FirstMiddleware())
    middleware_chain.add(SecondMiddleware())
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
        request_map=request_map,
        event_emitter=event_emitter,
        container=container,
        middleware_chain=middleware_chain,
    )

    await mediator.send(JoinMeetingRoomCommand(user_id=1))


if __name__ == "__main__":
    asyncio.run(main())
