from collections import defaultdict
from typing import Type, TypeVar

from diator.events.event import DomainEvent
from diator.events.event_handler import EventHandler

E_contra = TypeVar("E_contra", bound=DomainEvent, contravariant=True)


class EventMap:
    def __init__(self) -> None:
        self._event_map: dict[
            Type[DomainEvent], list[Type[EventHandler]]
        ] = defaultdict(lambda: [])

    def bind(
        self, event_type: Type[E_contra], handler_type: Type[EventHandler[E_contra]]
    ) -> None:
        self._event_map[event_type].append(handler_type)

    def get(self, event_type: Type[E_contra]) -> list[Type[EventHandler[E_contra]]]:
        return self._event_map[event_type]

    def get_events(self) -> list[Type[DomainEvent]]:
        return list(self._event_map.keys())
