from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Response:
    """
    Base class for response type objects.

    Response is a result of the request handling, which holded by RequestHandler.

    Often response is used for defining result of the query.

    Usage::

        @dataclass(frozen=True, kw_only=True)
        class ReadMeetingQueryResult(Response):
            meeting_id: int = field()
            link: str = field()
            status: MeetingStatusEnum = field()

    """
