import asyncio
from dataclasses import dataclass

from di import Container, bind_by_type
from di.dependent import Dependent
from redis import asyncio as redis

from diator.container.di import DIContainer
from diator.events import (
    DomainEvent,
    EventEmitter,
    EventHandler,
    EventMap,
    NotificationEvent,
)
from diator.mediator import Mediator
from diator.message_brokers.redis import RedisMessageBroker
from diator.middlewares import MiddlewareChain
from diator.requests import Request, RequestHandler, RequestMap


@dataclass(frozen=True, kw_only=True)
class JoinMeetingRoomCommand(Request):
    user_id: int


@dataclass(frozen=True, kw_only=True)
class UserJoinedDomainEvent(DomainEvent):
    user_id: int


@dataclass(frozen=True, kw_only=True)
class UserJoinedNotificationEvent(NotificationEvent):
    user_id: int


class JoinMeetingRoomCommandHandler(RequestHandler[JoinMeetingRoomCommand, None]):
    def __init__(self) -> None:
        self._events = []

    @property
    def events(self) -> list:
        return self._events

    async def handle(self, request: JoinMeetingRoomCommand) -> None:
        self._events.append(UserJoinedDomainEvent(user_id=request.user_id))
        self._events.append(UserJoinedNotificationEvent(user_id=123))


class UserJoinedEventHandler(EventHandler[UserJoinedDomainEvent]):
    async def handle(self, event: UserJoinedDomainEvent) -> None:
        print("READY", event)


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


def configure_di() -> DIContainer:
    container = Container()

    container.bind(bind_by_type(Dependent(UserJoinedEventHandler, scope="request"), UserJoinedEventHandler))
    container.bind(
        bind_by_type(
            Dependent(JoinMeetingRoomCommandHandler, scope="request"),
            JoinMeetingRoomCommandHandler,
        )
    )

    di_container = DIContainer()
    di_container.attach_external_container(container)

    return di_container


async def main() -> None:
    middleware_chain = MiddlewareChain()
    middleware_chain.add(FirstMiddleware())
    middleware_chain.add(SecondMiddleware())
    event_map = EventMap()
    event_map.bind(UserJoinedDomainEvent, UserJoinedEventHandler)
    request_map = RequestMap()
    request_map.bind(JoinMeetingRoomCommand, JoinMeetingRoomCommandHandler)
    container = configure_di()

    redis_client: redis.Redis = redis.Redis.from_url("redis://localhost:6379/0")

    event_emitter = EventEmitter(
        message_broker=RedisMessageBroker(redis_client),
        event_map=event_map,
        container=container,
    )

    mediator = Mediator(
        request_map=request_map,
        event_emitter=event_emitter,
        container=container,
        middleware_chain=middleware_chain,
    )

    await mediator.send(JoinMeetingRoomCommand(user_id=1))


if __name__ == "__main__":
    asyncio.run(main())
