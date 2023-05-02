import asyncio
from dataclasses import dataclass, field

from di import Container, bind_by_type
from di.dependent import Dependent

from diator.container.di import DIContainer
from diator.events import Event, EventEmitter, EventMap
from diator.mediator import Mediator
from diator.requests import Request, RequestHandler, RequestMap


@dataclass(frozen=True, kw_only=True)
class JoinMeetingCommand(Request):
    meeting_id: int
    user_id: int
    is_late: bool = field(default=False)


class JoinMeetingCommandHandler(RequestHandler[JoinMeetingCommand, None]):
    def __init__(self, meeting_api) -> None:
        self._meeting_api = meeting_api
        self._events: list[Event] = []

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: JoinMeetingCommand) -> None:
        self._meeting_api.join(request.meeting_id, request.user_id)
        if request.is_late:
            self._meeting_api.warn(request.user_id)


def setup_di() -> DIContainer:
    external_container = Container()

    external_container.bind(
        bind_by_type(
            Dependent(JoinMeetingCommandHandler, scope="request"),
            JoinMeetingCommandHandler,
        )
    )

    container = DIContainer()
    container.attach_external_container(external_container)

    return container


async def main() -> None:
    container = setup_di()

    request_map = RequestMap()
    request_map.bind(JoinMeetingCommand, JoinMeetingCommandHandler)

    event_emitter = EventEmitter(event_map=EventMap(), container=container, message_broker=None)

    mediator = Mediator(
        request_map=request_map,
        event_emitter=event_emitter,
        container=container,
    )

    await mediator.send(JoinMeetingCommand(user_id=1, meeting_id=1, is_late=True))


if __name__ == "__main__":
    asyncio.run(main())
