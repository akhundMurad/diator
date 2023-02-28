from typing import Protocol, Type
from diator.events.event_handler import EventHandler
from diator.generics import E_contra


class Consumer(Protocol):
    async def consume(self) -> None:
        ...

    def bind(
        self, event_type: Type[E_contra], event_handler: Type[EventHandler[E_contra]]
    ) -> None:
        ...
