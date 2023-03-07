import pytest
import redis.asyncio as redis

from diator.events.message_brokers.redis import RedisMessageBroker


@pytest.fixture()
def redis_client() -> redis.Redis:
    return redis.Redis.from_url("redis://redis:6379/0")


@pytest.fixture()
def redis_message_broker(redis_client: redis.Redis) -> RedisMessageBroker:
    return RedisMessageBroker(client=redis_client, channel_prefix="test_diator_channel")
