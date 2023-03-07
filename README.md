# Diator - CQRS Library for Python

Diator is a Python library for implementing CQRS pattern in your Python applications. It provides a set of abstractions and utilities to help you separate your read and write concerns, allowing for better scalability, performance, and maintainability of your application.

## Features

- Implements the CQRS pattern
- Simple, yet flexible API
- Works with Redis Pub/Sub (and will support the other message brokers)
- Easy to integrate with existing codebases
- Well-documented

## Installation

You can install Diator using pip:

```bash
pip install diator[redis]  # Currently only Redis is supported
```

## Basic usage


### Define Commands and Queries:
```python
from diator.requests.request import Request
from diator.response import Response


@dataclasses.dataclass(frozen=True, kw_only=True)
class JoinMeetingCommand(Request)
    meeting_id: int = dataclasses.field(default=1)
    user_id: int = dataclasses.field(default=1)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReadMeetingQuery(Request)
    meeting_id: int = dataclasses.field(default=1)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReadMeetingQueryResult(Response)
    meeting_id: int = dataclasses.field(default=1)
    link: str = dataclasses.field()

```

### Define Events:
```python
from diator.events.event import DomainEvent, NotificationEvent


@dataclasses.dataclass(frozen=True, kw_only=True)
class UserJoinedDomainEvent(Event):  # will be handled by special event handler
    user_id: int = dataclasses.field()
    meeting_id: int = dataclasses.field()
    timestamp: datetime = dataclasses.field()


@dataclasses.dataclass(frozen=True, kw_only=True)
class UserJoinedNotificationEvent(NotificationEvent):  # will be sent to a message broker
    user_id: int = dataclasses.field()

```

### Define Command and Event Handlers:
```python
from diator.requests.request_handler import RequestHandler
from diator.events.event_handler import EventHandler


class JoinMeetingCommandHandler(RequestHandler[JoinMeetingCommand, None]):  # Command Handler doesn't return anything
    def __init__(self, meeting_api: MeetingAPI) -> None:
        self._meeting_api = meeting_api
        self._events: list[Event] = []

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: JoinMeetingCommand) -> None:
        await self._meeting_api.join(request.meeting_id, request.user_id)
        self._events.append(
            UserJoinedDomainEvent(user_id=request.user_id, timestamp=datetime.utcnow(), meeting_id=request.meeting_id)
        )
        self._events.append(
            UserJoinedNotificationEvent(user_id=request.user_id)
        )


class UserJoinedDomainEventHandler(EventHandler[UserJoinedDomainEvent]):
    def __init__(self, meeting_api: MeetingAPI) -> None:
        self._meeting_api = meeting_api

    async def handle(self, event: UserJoinedDomainEvent) -> None:
        await self._meeting_api.notify(event.meeting_id, "New user joined!")


class ReadMeetingQueryHandler(RequestHandler[ReadMeetingQuery, ReadMeetingQueryResult]):  # Request Handler returns query result
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

### Build Mediator object
```python
from diator.requests.map import RequestMap
from diator.events.message_brokers.redis import RedisMessageBroker
from diator.events.event_emitter import EventEmitter
from diator.mediator import Mediator
from diator.events.map import EventMap


async def main() -> None:
    event_map = EventMap()
    event_map.bind(UserJoinedDomainEvent, UserJoinedDomainEventHandler)  # Mapping event to event handler
    request_map = RequestMap()
    request_map.bind(JoinMeetingCommand, JoinMeetingCommandHandler)  # Mapping command to command handler
    request_map.bind(ReadMeetingQuery, ReadMeetingQueryHandler)  # Mapping query to query handler

    redis_client = redis.Redis.from_url("redis://localhost:6379/0")  # Creating Async Redis Client

    event_emitter = EventEmitter(
        message_broker=RedisMessageBroker(redis_client),
        event_map=event_map,
        container=container,
    )

    mediator = Mediator(
        request_map=request_map, event_emitter=event_emitter, container=container
    )

    """ 
    1. JoinMeetingCommand is handled by JoinMeetingCommandHandler
    2. JoinMeetingCommandHandler publishes Domain and Notification Events
    3. UserJoinedDomainEvent is handled by UserJoinedDomainEventHandler
    4. UserJoinedNotificationEvent is sent to the Redis Pub/Sub
    """
    await mediator.send(JoinMeetingCommand(user_id=1))

    # Returns ReadMeetingQueryResult
    response = await mediator.send(ReadMeetingQuery(meeting_id=1))


if __name__ == "__main__":
    asyncio.run(main())

```

Redis Pub/Sub output:
```json
{
   "message_type":"notification_event",
   "message_name":"UserJoinedNotificationEvent",
   "message_id":"9f62e977-73f7-462b-92cb-8ea658d3bcb5",
   "payload":{
      "event_id":"9f62e977-73f7-462b-92cb-8ea658d3bcb5",
      "event_timestamp":"2023-03-07T09:26:02.588855",
      "user_id":123
   }
}
```
