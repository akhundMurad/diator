# Diator - CQRS Library for Python

Diator is a Python library for implementing CQRS pattern in your Python applications. It provides a set of abstractions and utilities to help you separate your read and write concerns, allowing for better scalability, performance, and maintainability of your application.

## Features :bulb:

- Implements the CQRS pattern
- Simple, yet flexible API
- Supports multiple message brokers, such as [Redis Pub/Sub](https://redis.io/docs/manual/pubsub/) and [Azure Service Bus](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview)
- Easy to integrate with existing codebases

## Installation :triangular_ruler:

Install the Diator library with [pip](https://pypi.org/project/diator/)

- To use Redis as Message Broker

    ```bash
    pip install diator[redis]
    ```

- Or Azure Service Bus

    ```bash
    pip install diator[azure]
    ```

## Documentation :blue_book:

To use the Diator library, there are several components to familiarize yourself with. These include Commands and Command Handlers, Queries and Query Handlers, Events and Event Handlers, and Message Brokers. By utilizing these components, you can effectively manage the exchange of information between the read and write models in your application.

### **Commands and Command Handlers**

**Command** represents an intention to perform an action or change the state of an application. Here is an example of the Command:

```python
from diator.requests import Request
from diator.response import Response


@dataclasses.dataclass(frozen=True, kw_only=True)
class JoinMeetingCommand(Request)
    meeting_id: int = dataclasses.field(default=1)
    user_id: int = dataclasses.field(default=1)

```

**Command Handler** is a component responsible for handling a Command and executing the corresponding action:

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
        self._events.append(
            UserJoinedDomainEvent(user_id=request.user_id, timestamp=datetime.utcnow(), meeting_id=request.meeting_id)
        )
        self._events.append(
            UserJoinedNotificationEvent(user_id=request.user_id)
        )

```

### **Queries and Query Handlers**

**Query** represents a request for information or data from the application's read model. The process of handling queries **SHOULD NOT** modify the state of the application:

```python
from diator.requests import Request


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReadMeetingQuery(Request)
    meeting_id: int = dataclasses.field(default=1)

```

**Query Result** is an object that contains the data requested by a Query. It is returned by a Query Handler after it processes a Query against the read model:

```python
from diator.response import Response

@dataclasses.dataclass(frozen=True, kw_only=True)
class ReadMeetingQueryResult(Response)
    meeting_id: int = dataclasses.field(default=1)
    link: str = dataclasses.field()

```

**Query Handler** is a component responsible for processing a Query against the read model and returning the requested data as a Query Result:

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

### **Events and Event Handlers**

**Event** represents a fact that has occurred in the application. It typically represents a significant change in the application's state that is of interest to other parts of the application or external systems.
There are several event types:

- **Domain Event** - is a message describing a significant event that has
occurred in the business domain.
- **Notification Event** - is a message regarding a change in the business domain that other components will react to.
- **Event-carried state transfer (ECST)** - messages notify subscribers about changes in the producer’s internal state.

```python
from diator.events import DomainEvent, NotificationEvent, ECSTEvent


@dataclasses.dataclass(frozen=True, kw_only=True)
class UserJoinedDomainEvent(Event):  # will be handled by an event handler
    user_id: int = dataclasses.field()
    meeting_id: int = dataclasses.field()
    timestamp: datetime = dataclasses.field()


@dataclasses.dataclass(frozen=True, kw_only=True)
class UserJoinedNotificationEvent(NotificationEvent):  # will be sent to a message broker
    user_id: int = dataclasses.field()


@dataclasses.dataclass(frozen=True, kw_only=True)
class UserChangedECSTEvent(ECSTEvent):  # will be sent to a message broker
    user_id: int = dataclasses.field()
    new_username: str = dataclasses.field()

```

**Event Handler** is a component responsible for processing an Event that has occurred in the application:

```python
from diator.events import EventHandler

class UserJoinedDomainEventHandler(EventHandler[UserJoinedDomainEvent]):
    def __init__(self, meeting_api: MeetingAPI) -> None:
        self._meeting_api = meeting_api

    async def handle(self, event: UserJoinedDomainEvent) -> None:
        await self._meeting_api.notify(event.meeting_id, "New user joined!")
```

Also the diator library supports different message brokers:

- Redis Pub/Sub (`diator.message_brokers.redis.RedisMessageBroker`)
- Azure Service Bus (`diator.message_brokers.azure.AzureMessageBroker`)

### **Dependency Injection**

Currently the library supports only di frameworks like [di](https://github.com/adriangb/di) and [rodi](https://github.com/Neoteroi/rodi)

Example of the rodi usage:

```python
from rodi import Container
from diator.container.rodi import RodiContainer


def setup_di() -> RodiContainer:
    external_container = Container()

    external_container.register(UserJoinedDomainEventHandler)
    external_container.register(JoinMeetingCommandHandler)
    external_container.register(ReadMeetingQueryHandler)

    container = RodiContainer()
    container.attach_external_container(external_container)

    return container

```

Example of the di lib usage:

```python
from di import Container, bind_by_type  # using di lib as di-framework
from diator.container.di import DIContainer


def setup_di() -> DIContainer:
    external_container = Container()

    external_container.bind(
        bind_by_type(
            Dependent(UserJoinedDomainEventHandler, scope="request"), 
            UserJoinedDomainEventHandler
        )
    )
    external_container.bind(
        bind_by_type(
            Dependent(JoinMeetingCommandHandler, scope="request"),
            JoinMeetingCommandHandler,
        )
    )
    external_container.bind(
        bind_by_type(
            Dependent(ReadMeetingQueryHandler, scope="request"),
            ReadMeetingQueryHandler,
        )
    )

    container = DIContainer()
    container.attach_external_container(external_container)

    return container

```

### **Middlewares**

```python
from diator.requests import Request


class SomeMiddleware:
    async def __call__(request: Request, handle):
        """
        Some logic related to request part of the circle.
        """

        response = await handle(request)

        """
        Some logic related to response part of the circle.
        """
        return response

```

### **Putting it all together** :nut_and_bolt:

```python
from diator.requests import RequestMap
from diator.message_brokers.redis import RedisMessageBroker
from diator.events import EventEmitter
from diator.mediator import Mediator
from diator.events import EventMap
from diator.middlewares import MiddlewareChain


async def main() -> None:
    container = setup_di()

    event_map = EventMap()
    event_map.bind(UserJoinedDomainEvent, UserJoinedDomainEventHandler)  # Mapping event to event handler
    request_map = RequestMap()
    request_map.bind(JoinMeetingCommand, JoinMeetingCommandHandler)  # Mapping command to command handler
    request_map.bind(ReadMeetingQuery, ReadMeetingQueryHandler)  # Mapping query to query handler

    redis_client = redis.Redis.from_url("redis://localhost:6379/0")  # Creating Async Redis Client

    middleware_chain = MiddlewareChain()
    middleware_chain.add(SomeMiddleware())  # Adding Middleware to a chain

    event_emitter = EventEmitter(
        message_broker=RedisMessageBroker(redis_client),
        event_map=event_map,
        container=container,
    )

    mediator = Mediator(
        request_map=request_map, 
        event_emitter=event_emitter, 
        container=container, 
        middleware_chain=MiddlewareChain
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

## Further reading :scroll:

- [Udi Dahan - Clarified CQRS](https://udidahan.com/2009/12/09/clarified-cqrs/)
- [Martin Fowler - CQRS](https://martinfowler.com/bliki/CQRS.html)
- [Marting Fowler - What do you mean by “Event-Driven”?](https://martinfowler.com/articles/201701-event-driven.html)
- [Vlad Khononov - Learning Domain-Driven Design](https://www.oreilly.com/library/view/learning-domain-driven-design/9781098100124/)
- [Vaughn Vernon - Really Simple CQRS](https://kalele.io/really-simple-cqrs/)

## License

This project is licensed under the terms of the MIT license.
