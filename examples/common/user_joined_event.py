from dataclasses import dataclass, field

from diator.events.event import Event


@dataclass(frozen=True, kw_only=True)
class UserJoinedEvent(Event):
    user_id: int = field()
