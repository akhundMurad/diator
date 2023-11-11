import logging

import orjson
import aio_pika
import asyncio
from diator.message_brokers.protocol import Message


        
class RabbitMQMessageBroker:
    def __init__(self, client, *, routing_key: str | None = None, exchange: str | None = None) -> None:
        self._connection = client
        self._routing_key = routing_key 
        self._exchange = exchange 

    async def send_message(self, message: Message) -> None:
        async with self._connection as connection:
            
            channel = await connection.channel()
            if self._exchange:
                await channel.basic_publish(exchange=self._exchange,body=aio_pika.Message(body=orjson.dumps(message)),routing_key=self._routing_key)
            else:
                await channel.default_exchange.publish(aio_pika.Message(body=orjson.dumps(message)),routing_key=self._routing_key)
