import asyncio
from redis import asyncio as redis

from src.diator.events.consumer.redis import RedisConsumer
from src.diator.events.map import EventMap
from examples.common.user_joined_event import UserJoinedEvent
from examples.common.user_joined_event_handler import UserJoinedEventHandler
from examples.common.container import Container


async def consume() -> None:
    event_map = EventMap()
    event_map.bind(UserJoinedEvent, UserJoinedEventHandler)

    redis_client = redis.Redis.from_url("redis://localhost:6379/0")

    consumer = RedisConsumer(
        event_map=event_map, container=Container(), redis_client=redis_client
    )

    await consumer.consume()


if __name__ == "__main__":
    asyncio.run(consume())
