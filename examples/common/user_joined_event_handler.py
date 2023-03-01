from examples.common.user_joined_event import UserJoinedEvent

from src.diator.events.event_handler import EventHandler


class UserJoinedEventHandler(EventHandler[UserJoinedEvent]):
    async def handle(self, event: UserJoinedEvent) -> None:
        print("READY", event)
