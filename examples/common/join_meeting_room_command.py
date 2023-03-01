from dataclasses import dataclass, field

from src.diator.requests.request import Request


@dataclass(frozen=True, kw_only=True)
class JoinMeetingRoomCommand(Request):
    user_id: int = field()
