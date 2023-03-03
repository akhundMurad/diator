from examples.common.join_meeting_room_command import JoinMeetingRoomCommand
from examples.common.user_joined_domain_event import UserJoinedDomainEvent
from examples.common.user_joined_notification_event import UserJoinedNotificationEvent
from diator.requests.request_handler import RequestHandler


class JoinMeetingRoomCommandHandler(RequestHandler[JoinMeetingRoomCommand, None]):
    def __init__(self) -> None:
        self._events = []

    @property
    def events(self) -> list:
        return self._events

    async def handle(self, request: JoinMeetingRoomCommand) -> None:
        self._events.append(UserJoinedDomainEvent(user_id=request.user_id))
        self._events.append(UserJoinedNotificationEvent(user_id=123))