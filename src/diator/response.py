from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Response:
    """
    Base class for response type objects.

    The response is a result of the request handling, which hold by RequestHandler.

    Often the response is used for defining the result of the query.

    Usage::

        @dataclass(frozen=True, kw_only=True)
        class ReadMeetingQueryResult(Response):
            meeting_id: int = field()
            link: str = field()
            status: MeetingStatusEnum = field()

    """
