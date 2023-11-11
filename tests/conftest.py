import pytest
import redis.asyncio as redis
import aio_pika

from diator.message_brokers.redis import RedisMessageBroker
from diator.message_brokers.rabbitmq import RabbitMQMessageBroker
@pytest.fixture()
def redis_client() -> redis.Redis:
    return redis.Redis.from_url("redis://localhost:6379/0")


@pytest.fixture()
def redis_message_broker(redis_client: redis.Redis) -> RedisMessageBroker:
    return RedisMessageBroker(client=redis_client, channel_prefix="test_diator_channel")

@pytest.fixture()
async def rabbitmq_client() -> aio_pika.Connection:
    connection = await aio_pika.connect_robust()
    return connection

@pytest.fixture()
async def rabbitmq_client_subs() -> aio_pika.Connection:
    connection = await aio_pika.connect_robust(client_properties={"connection_name": "caller"})
    return connection

@pytest.fixture()
def rabbitmq_message_broker(rabbitmq_client: aio_pika.Connection) -> RabbitMQMessageBroker:
    return RabbitMQMessageBroker(client=rabbitmq_client, routing_key="test_diator_queue")