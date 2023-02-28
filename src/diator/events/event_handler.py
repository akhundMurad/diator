from typing import Protocol

from diator.generics import E_contra


class EventHandler(Protocol[E_contra]):
    async def handle(self, event: E_contra) -> None:
        raise NotImplementedError
