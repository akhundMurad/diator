# Requests

This section will guide you to the way of working with requests and responses.

There are two types of requests in the CQRS: `Command`, `Query`.

## Command

Command represents an intention to perform an action or change the state of an application. Here is an example of the Command:

```python
from diator.requests import Request
from diator.response import Response


@dataclasses.dataclass(frozen=True, kw_only=True)
class JoinMeetingCommand(Request)
    meeting_id: int = dataclasses.field(default=1)
    user_id: int = dataclasses.field(default=1)
```

We define `frozen=True`, since all requests should be immutable by definition.

### Command Handler

Command Handler is a component responsible for handling a Command and executing the corresponding action:

```python
from diator.requests import RequestHandler
from diator.events import EventHandler


class JoinMeetingCommandHandler(RequestHandler[JoinMeetingCommand, None]):
    def __init__(self, meeting_api: MeetingAPI) -> None:
        self._meeting_api = meeting_api
        self._events: list[Event] = []

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: JoinMeetingCommand) -> None:
        await self._meeting_api.join(request.meeting_id, request.user_id)
```

## Query

Query represents a request for information or data from the application's read model. The process of handling queries **SHOULD NOT** modify the state of the application:

```python
from diator.requests import Request


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReadMeetingQuery(Request)
    meeting_id: int = dataclasses.field(default=1)
```

### Query Result

Query Result is an object that contains the data requested by a Query. It is returned by a Query Handler after it processes a Query against the read model:

```python
from diator.response import Response

@dataclasses.dataclass(frozen=True, kw_only=True)
class ReadMeetingQueryResult(Response)
    meeting_id: int = dataclasses.field(default=1)
    link: str = dataclasses.field()
```

### Query Handler

Query Handler is a component responsible for processing a Query against the read model and returning the requested data as a Query Result:

```python
from diator.requests import RequestHandler


class ReadMeetingQueryHandler(RequestHandler[ReadMeetingQuery, ReadMeetingQueryResult]):
    def __init__(self, meeting_api: MeetingAPI) -> None:
        self._meeting_api = meeting_api
        self._events: list[Event] = []

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: ReadMeetingQuery) -> ReadMeetingQueryResult:
        link = await self._meeting_api.get_link(request.meeting_id)
        return ReadMeetingQueryResult(
            meeting_id=request.meeting_id,
            link=link
        )
```

## Mapping

In order to map each request to its handler, you can use `RequestMap` as below:

```python
from diator.requests import RequestMap


request_map = RequestMap()
request_map.bind(JoinMeetingCommand, JoinMeetingCommandHandler)
request_map.bind(ReadMeetingQuery, ReadMeetingQueryHandler)

```

And then, put it to `Mediator`:

```python hl_lines="9"
from diator.mediator import Mediator
from diator.requests import RequestMap


request_map = RequestMap()
request_map.bind(JoinMeetingCommand, JoinMeetingCommandHandler)
request_map.bind(ReadMeetingQuery, ReadMeetingQueryHandler)

mediator = Mediator(request_map=request_map, container=container)
```
