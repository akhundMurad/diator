from typing import Protocol, TypeVar

from diator.events.event import DomainEvent

E = TypeVar("E", bound=DomainEvent, contravariant=True)


class EventHandler(Protocol[E]):
    async def handle(self, event: E) -> None:
        raise NotImplementedError
