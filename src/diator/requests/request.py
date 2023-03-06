from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class Request:
    """
    Base class for request-type objects.

    The request is an input of the request handler.
    Often Request is used for defining queries or commands.

    Usage::

      @dataclass(frozen=True, kw_only=True)
      class JoinMeetingCommand(Request):
          meeting_id: int = field()
          user_id: int = field()

      @dataclass(frozen=True, kw_only=True)
      class ReadMeetingByIdQuery(Request):
          meeting_id: int = field()

    """

    request_id: UUID = field(default_factory=uuid4)
