import redis.asyncio as redis

from diator.events.message_brokers.redis import RedisMessageBroker, Message


async def test_redis_message_broker_publish_event(
    redis_message_broker: RedisMessageBroker, redis_client: redis.Redis
) -> None:
    async with redis_client.pubsub() as pubsub:
        await pubsub.psubscribe("test_diator_channel:*")

        message = Message(payload="hello")
        await redis_message_broker.send_message(message=message)
        await pubsub.get_message(ignore_subscribe_messages=True)
        message = await pubsub.get_message(ignore_subscribe_messages=True)

        assert message
        assert message["data"] == b"hello"
