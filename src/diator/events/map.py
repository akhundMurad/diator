from collections import defaultdict
from typing import Type

from diator.events.event import Event
from diator.events.event_handler import EventHandler
from diator.generics import E_contra


class EventMap:
    def __init__(self) -> None:
        self._event_map: dict[Type[Event], list[Type[EventHandler]]] = defaultdict(
            lambda: []
        )

    def bind(
        self, event_type: Type[E_contra], handler_type: Type[EventHandler[E_contra]]
    ) -> None:
        self._event_map[event_type].append(handler_type)

    def get(self, event_type: Type[E_contra]) -> list[Type[EventHandler[E_contra]]]:
        return self._event_map[event_type]

    def get_events(self) -> list[Type[Event]]:
        return list(self._event_map.keys())
