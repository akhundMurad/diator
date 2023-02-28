from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class Message:
    message_id: UUID = field(default_factory=uuid4)
    payload: str = field()


class MessageBroker(Protocol):
    async def send_message(self, message: Message) -> None:
        ...
