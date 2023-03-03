from dataclasses import dataclass, field

from diator.events.event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class UserJoinedDomainEvent(DomainEvent):
    user_id: int = field()
