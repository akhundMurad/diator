from examples.common.user_joined_domain_event import UserJoinedDomainEvent

from diator.events.event_handler import EventHandler


class UserJoinedEventHandler(EventHandler[UserJoinedDomainEvent]):
    async def handle(self, event: UserJoinedDomainEvent) -> None:
        print("READY", event)
