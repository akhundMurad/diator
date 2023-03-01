import asyncio
from redis import asyncio as redis

from examples.common.join_meeting_room_command import JoinMeetingRoomCommand
from examples.common.join_meeting_room_command_handler import (
    JoinMeetingRoomCommandHandler,
)
from examples.common.container import Container

from src.diator.requests.map import RequestMap
from src.diator.events.message_brokers.redis import RedisMessageBroker
from src.diator.events.event_emitter import EventEmitter
from src.diator.mediator import Mediator


async def main() -> None:
    request_map = RequestMap()
    request_map.bind(JoinMeetingRoomCommand, JoinMeetingRoomCommandHandler)

    redis_client = redis.Redis.from_url("redis://localhost:6379/0")

    event_emitter = EventEmitter(RedisMessageBroker(redis_client))

    mediator = Mediator(
        request_map=request_map, event_emitter=event_emitter, container=Container()
    )

    await mediator.send(JoinMeetingRoomCommand(user_id=1))


if __name__ == "__main__":
    asyncio.run(main())
