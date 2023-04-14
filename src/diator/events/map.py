from collections import defaultdict
from typing import Type, TypeVar

from diator.events.event import DomainEvent
from diator.events.event_handler import EventHandler

E = TypeVar("E", bound=DomainEvent, contravariant=True)


class EventMap:
    def __init__(self) -> None:
        self._event_map: dict[Type[DomainEvent], list[Type[EventHandler]]] = defaultdict(lambda: [])

    def bind(self, event_type: Type[E], handler_type: Type[EventHandler[E]]) -> None:
        self._event_map[event_type].append(handler_type)

    def get(self, event_type: Type[E]) -> list[Type[EventHandler[E]]]:
        return self._event_map[event_type]

    def get_events(self) -> list[Type[DomainEvent]]:
        return list(self._event_map.keys())

    def __str__(self) -> str:
        return str(self._event_map)
