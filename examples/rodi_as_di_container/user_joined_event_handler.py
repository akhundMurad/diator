from .user_joined_domain_event import UserJoinedDomainEvent

from diator.events import EventHandler


class UserJoinedEventHandler(EventHandler[UserJoinedDomainEvent]):
    async def handle(self, event: UserJoinedDomainEvent) -> None:
        print("READY", event)
