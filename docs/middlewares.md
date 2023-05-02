# Middlewares

A middleware is a component that wraps request handler in order to observe or change its behavior.

## Usage

Generally, your middleware should match the following protocol:

```python
class Middleware(Protocol):
    async def __call__(self, request: Request, handle: HandleType) -> Res:
        ...
```

The simplest sample:

```python
class SampleMiddleware:
    async def __call__(self, request: Request, handle):
        print("Before handle: ", request)
        response = await handle(request)
        print("After handle: ", response)
```

### Middleware chain

A middleware chain is a crucial component that serves as a storage for your middlewares. It simplifies the interaction between middleware and request handlers.

Usage:

```python
from diator.middlewares import MiddlewareChain


class FirstMiddleware:
    async def __call__(self, request: Request, handle):
        print("Before 1 handling...")
        response = await handle(request)
        print("After 1 handling...")
        return response


class SecondMiddleware:
    async def __call__(self, request: Request, handle):
        print("Before 2  handling...")
        response = await handle(request)
        print("After 2 handling...")
        return response


middleware_chain = MiddlewareChain()
middleware_chain.add(FirstMiddleware())
middleware_chain.add(SecondMiddleware())

mediator = Mediator(
    request_map=request_map,
    container=container,
    middleware_chain=middleware_chain,
)
```

Output will be the following:

```bash
Before 1 handling...
Before 2  handling...
After 2 handling...
After 1 handling...
```


## Built-in middlewares

We plan to provide several middlewares for common use cases. Currently, only logging middleware is implemented.

### Logging

Simply import it:

```python
from diator.middlewares import LoggingMiddleware
```

And then add it to the `MiddlewareChain`:

```python
from diator.middlewares import MiddlewareChain
from diator.middlewares.logging import LoggingMiddleware


chain = MiddlewareChain()
chain.add(LoggingMiddleware())
```

Result:

```bash
DEBUG:diator.middlewares.logging:Request JoinMeetingRoomCommand handled. Response: None
DEBUG:diator.events.event_emitter:Sending Notification Event(a9aab9b3-6a40-4caa-ba63-93d3f92bb11b) to message broker RedisMessageBroker
DEBUG:diator.message_brokers.redis:Sending message to Redis Pub/Sub a9aab9b3-6a40-4caa-ba63-93d3f92bb11b.
DEBUG:diator.events.event_emitter:Handling Event(UserJoinedDomainEvent) via event handler(UserJoinedEventHandler)
```
