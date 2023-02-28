import logging
import orjson

from diator.events.event import Event
from diator.events.message_brokers.protocol import MessageBroker, Message


logger = logging.getLogger(__name__)


class EventEmitter:
    def __init__(self, message_broker: MessageBroker) -> None:
        self._message_broker = message_broker

    async def emit(self, event: Event) -> None:
        message = _build_message(event)

        logger.info(
            "Sending event(%s) to message broker %s",
            event.event_id,
            type(self._message_broker).__name__,
        )

        await self._message_broker.send_message(message)


def _build_message(event: Event) -> Message:
    return Message(
        message_id=event.event_id,
        payload=orjson.dumps(event).decode(),
        event_type=type(event).__name__,
    )
