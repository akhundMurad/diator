from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class Message:
    message_type: str = field()
    message_name: str = field()
    message_id: UUID = field(default_factory=uuid4)
    payload: dict = field()


class MessageBroker(Protocol):
    """
    The interface over a message broker.

    Used for sending messages to message brokers (currently only redis supported).
    """

    async def send_message(self, message: Message) -> None:
        ...
