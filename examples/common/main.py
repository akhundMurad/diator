import asyncio
from redis import asyncio as redis

from examples.common.join_meeting_room_command import JoinMeetingRoomCommand
from examples.common.join_meeting_room_command_handler import (
    JoinMeetingRoomCommandHandler,
)
from examples.common.container import Container
from examples.common.user_joined_domain_event import UserJoinedDomainEvent
from examples.common.user_joined_event_handler import UserJoinedEventHandler

from diator.requests.map import RequestMap
from diator.events.message_brokers.redis import RedisMessageBroker
from diator.events.event_emitter import EventEmitter
from diator.mediator import Mediator
from diator.events.map import EventMap


async def main() -> None:
    event_map = EventMap()
    event_map.bind(UserJoinedDomainEvent, UserJoinedEventHandler)
    request_map = RequestMap()
    request_map.bind(JoinMeetingRoomCommand, JoinMeetingRoomCommandHandler)

    redis_client = redis.Redis.from_url("redis://localhost:6379/0")

    event_emitter = EventEmitter(
        message_broker=RedisMessageBroker(redis_client),
        event_map=event_map,
        container=Container(),
    )

    mediator = Mediator(
        request_map=request_map, event_emitter=event_emitter, container=Container()
    )

    await mediator.send(JoinMeetingRoomCommand(user_id=1))


if __name__ == "__main__":
    asyncio.run(main())
