# Events

Event represents a fact that has occurred in the application. It typically represents a significant change in the application's state that is of interest to other parts of the application or external systems.

There are several types of events:

- Domain event
- Notification event
- Event-carried state transfer (ECST)

Domain events are handled by specialized handlers, whereas Notification and ECST events are sent to message brokers.

## Publishing Event

Events are published in the `CommandHandler` side like below:

```python hl_lines="16-21"
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

## Domain Event

Domain event is a message describing a significant event that has occurred in the business domain.

Example:

```python
from diator.events import DomainEvent


@dataclasses.dataclass(frozen=True, kw_only=True)
class UserJoinedDomainEvent(DomainEvent):
    user_id: int = dataclasses.field()
    meeting_id: int = dataclasses.field()
    timestamp: datetime = dataclasses.field()
```

This event type is handled by its event handler.

### Event Handler

Event Handler is a component responsible for processing an Domain Event that has occurred in the application:

```python
from diator.events import EventHandler


class UserJoinedDomainEventHandler(EventHandler[UserJoinedDomainEvent]):
    def __init__(self, meeting_api: MeetingAPI) -> None:
        self._meeting_api = meeting_api

    async def handle(self, event: UserJoinedDomainEvent) -> None:
        await self._meeting_api.notify(event.meeting_id, "New user joined!")
```

### Mapping

In order to map each domain event to its handler, you can use `EventMap` as below:

```python
from diator.requests import EventMap


event_map = EventMap()
event_map.bind(UserJoinedDomainEvent, UserJoinedDomainEventHandler)
event_map.bind(UserJoinedDomainEvent, AnotherUserJoinedDomainEventHandler)
```

## Notification Event

Notification Event is a message regarding a change in the business domain that other components will react to.

Example:

```python
from diator.events import NotificationEvent


@dataclasses.dataclass(frozen=True, kw_only=True)
class UserJoinedNotificationEvent(NotificationEvent):
    user_id: int = dataclasses.field()
```

## ECST Event

Event-carried state transfer (ECST) is a message that notifies subscribers about changes in the producer’s internal state.

Example:

```python
from diator.events import ECSTEvent


@dataclasses.dataclass(frozen=True, kw_only=True)
class UserChangedECSTEvent(ECSTEvent):
    user_id: int = dataclasses.field()
    new_username: str = dataclasses.field()
```

## Event Emitter

`EventEmitter` is a component, that is responsible for events dispatching. It decides whether to send event to message broker or dispatch it using handler.

Here is a simple `EventEmitter` usage:

```python
from diator.events import EventMap, EventEmitter
from diator.mediator import Mediator


event_map = EventMap()
event_map.bind(UserJoinedDomainEvent, UserJoinedDomainEventHandler)
event_map.bind(UserJoinedDomainEvent, AnotherUserJoinedDomainEventHandler)

event_emitter = EventEmitter(event_map=event_map, container=container)
mediator = Mediator(
    event_emitter=event_emitter,
    request_map=request_map,
    container=container
)

```

## Message Broker

Diator supports several message brokers to publish Notification and ECST events.
Supported message brokers:

- [Redis Pub/Sub](https://redis.io/docs/manual/pubsub/)
- [Azure Service Bus](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview)

### Redis

To use Redis Pub/Sub as message broker, simply import it and put to `EventEmitter`:

```python
from redis.asyncio import Redis
from diator.events import EventMap, EventEmitter
from diator.message_brokers.redis import RedisMessageBroker


redis_client = Redis()

message_broker = RedisMessageBroker(client=redis_client)

event_emitter = EventEmitter(
    event_map=event_map, 
    container=container,
    message_broker=message_broker
)
```

As a result, it will produce events in the channel with default prefix `python_diator_channel`.

Example of published event:

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

Channel name:

```bash
python_diator_channel:notification_event:9f62e977-73f7-462b-92cb-8ea658d3bcb5
```

So, you can listen to specific event types by defining pattern of channel:

```bash
PSUBSCRIBE python_diator_channel:notification_event:*
```

### Azure Service Bus

To use Azure Service Bus as message broker, simply import it and put to `EventEmitter`:

```python
from azure.servicebus.aio import ServiceBusClient
from diator.events import EventMap, EventEmitter
from diator.message_brokers.azure import AzureMessageBroker


azure_service_bus_client = ServiceBusClient.from_connection_string(
    service_bus_connection_string
)
message_broker = AzureMessageBroker(
    azure_service_bus_client,
    topic_name,
    timeout=15
)

event_emitter = EventEmitter(
    event_map=event_map, 
    container=container,
    message_broker=message_broker
)
```
