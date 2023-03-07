import json

import redis.asyncio as redis

from diator.events.message_brokers.redis import Message, RedisMessageBroker


async def test_redis_message_broker_publish_event(
    redis_message_broker: RedisMessageBroker, redis_client: redis.Redis
) -> None:
    async with redis_client.pubsub() as pubsub:
        await pubsub.psubscribe("test_diator_channel:*")

        message = Message(payload={"phrase": "hello"}, message_type="", message_name="")
        await redis_message_broker.send_message(message=message)
        await pubsub.get_message(ignore_subscribe_messages=True)
        pubsub_data: dict = await pubsub.get_message(ignore_subscribe_messages=True)

        assert pubsub_data

        data = json.loads(pubsub_data["data"].decode())

        assert "message_type" in data
        assert "message_id" in data
        assert data["payload"] == {"phrase": "hello"}
