from dataclasses import dataclass

from diator.events import NotificationEvent


@dataclass(frozen=True, kw_only=True)
class UnactiveUsersCleaned(NotificationEvent):
    ids: list
