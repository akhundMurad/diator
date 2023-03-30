from dataclasses import dataclass, field

from diator.events import NotificationEvent


@dataclass(frozen=True, kw_only=True)
class UserJoinedNotificationEvent(NotificationEvent):
    user_id: int = field()
