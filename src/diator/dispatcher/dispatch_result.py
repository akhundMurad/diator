from typing import TypedDict

from diator.events.event import Event
from diator.response import Response


class DispatchResult(TypedDict):
    response: Response | None
    events: list[Event]