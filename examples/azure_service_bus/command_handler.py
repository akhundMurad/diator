from diator.requests import RequestHandler
from examples.azure_service_bus.event import UnactiveUsersCleaned

from .command import CleanUnactiveUsersCommand


class CleanUnactiveUsersCommandHandler(RequestHandler[CleanUnactiveUsersCommand, None]):
    def __init__(self) -> None:
        self._events = []

    @property
    def events(self) -> list:
        return self._events

    async def handle(self, request: CleanUnactiveUsersCommand) -> None:
        self._events.append(UnactiveUsersCleaned(ids=[1, 2, 3, 4, 5]))
