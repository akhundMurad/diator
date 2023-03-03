from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class Event:
    ...


@dataclass(frozen=True, kw_only=True)
class DomainEvent(Event):
    ...


@dataclass(frozen=True, kw_only=True)
class NotificationEvent(Event):
    event_id: UUID = field(default_factory=uuid4)
    event_timestamp: datetime = field(default_factory=datetime.utcnow)
    _event_type = "notification_event"


@dataclass(frozen=True, kw_only=True)
class ECSTEvent(Event):
    event_id: UUID = field(default_factory=uuid4)
    event_timestamp: datetime = field(default_factory=datetime.utcnow)
    _event_type = "ecst_event"
