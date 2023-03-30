from dataclasses import dataclass, field

from diator.events.event import Event
from diator.response import Response


@dataclass
class DispatchResult:
    response: Response | None = field(default=None)
    events: list[Event] = field(default_factory=list)
