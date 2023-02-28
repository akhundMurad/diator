from typing import Protocol, TypeVar

from diator.events.event import Event


E = TypeVar("E", bound=Event, contravariant=True)


class EventHandler(Protocol[E]):
    async def handle(self, event: E) -> None:
        raise NotImplementedError
