# Architecture

## Components

Structure of the library includes several components, such as:

- `Request`
- `RequestMap`
- `RequestHandler`
- `Response`
- `Event`
- `EventMap`
- `EventHandler`
- `MessageBroker`
- `EventEmitter`
- `Container`
- `Dispatcher`
- `Middleware`
- `MiddlewareChain`
- `Mediator`

## Components Dependency

### Request-related system side:

```mermaid
classDiagram
    Dispatcher <|-- Mediator
    MiddlewareChain <|-- Dispatcher
    RequestMap <|-- Dispatcher

    class RequestMap{
        +bind(request_type, handler_type) None
        +get(request_type) Type[RequestHandler]
    }
    class MiddlewareChain{
        +set(chain) None
        +add(middleware) None
        +wrap(handler) WrappedHandler
    }
    class Dispatcher{
        +RequestMap request_map
        +Container container
        +MiddlewareChain middleware_chain
        +dispatch(request) DispatchResult
    }
    class Mediator{
        +RequestMap request_map
        +Container container
        +MiddlewareChain middleware_chain
        +EventEmitter event_emitter
        +send(request) Response
    }
```

### Event-related system side:

```mermaid
classDiagram
    EventEmitter <|-- Mediator
    EventMap <|-- EventEmitter
    MessageBroker <|-- EventEmitter

    class EventMap{
        +bind(event_type, handler_type) None
        +get(event_type) List[Type[EventHandler]]
    }
    class MessageBroker{
        +send_message(message) None
    }
    class EventEmitter{
        +EventMap event_map
        +Container container
        +MessageBroker message_broker
        +emit(event) None
    }
    class Mediator{
        +RequestMap request_map
        +Container container
        +MiddlewareChain middleware_chain
        +EventEmitter event_emitter
        +send(request) Response
    }
```

## Components Interaction

### Request dispatching:

```mermaid
graph TB
    Client-- JoinMeetingCommand -->Mediator-->Dispatcher-- JoinMeetingCommand -->JoinMeetingCommandHandler
```

Description:

1. Client sends JoinMeetingCommand to Mediator.
2. Mediator sends this command to Dispatcher.
3. Dispatcher gets its handler and builds instance of command handler class via Container.
4. Dispatcher handles command using certain method of its handler.
5. Dispatcher returns DispatchResult to Mediator, which contains published events and Response.

### Event dispatching:

```mermaid
graph TB
    Dispatcher-- UserJoinedEvent -->Mediator-->EventEmitter-- UserJoinedEvent -->UserJoinedEventHandler
```

Description:

1. Dispatcher returns DispatchResult to Mediator, which contains published events and Response.
2. Mediator sends published event to EventEmitter.
3. Event gets its handler and builds instance of event handler class via Container.
4. EventEmitter handles command using certain method of its handler.
