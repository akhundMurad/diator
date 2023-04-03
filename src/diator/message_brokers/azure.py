import orjson
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

from diator.message_brokers.protocol import Message


class AzureMessageBroker:
    def __init__(self, client: ServiceBusClient, topic_name: str, *, timeout: float | None = None) -> None:
        self._client = client
        self._topic_name = topic_name
        self._timeout = timeout

    async def send_message(self, message: Message) -> None:
        async with self._client:
            sender = self._client.get_topic_sender(self._topic_name)

            service_bus_message = _parse_message(message)

            await sender.send_messages(service_bus_message, timeout=self._timeout)


def _parse_message(message: Message) -> ServiceBusMessage:
    return ServiceBusMessage(orjson.dumps(message), content_type="application/json")
