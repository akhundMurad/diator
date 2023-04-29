import asyncio
import logging
from dataclasses import dataclass

from redis import asyncio as redis
from rodi import Container

from diator.container.rodi import RodiContainer
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
from diator.middlewares.logging import LoggingMiddleware
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


def configure_di() -> RodiContainer:
    container = Container()

    container.register(UserJoinedEventHandler)
    container.register(JoinMeetingRoomCommandHandler)

    rodi_container = RodiContainer()
    rodi_container.attach_external_container(container)

    return rodi_container


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


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    middleware_chain = MiddlewareChain()
    middleware_chain.add(LoggingMiddleware())
    middleware_chain.add(FirstMiddleware())
    middleware_chain.add(SecondMiddleware())
    event_map = EventMap()
    event_map.bind(UserJoinedDomainEvent, UserJoinedEventHandler)
    request_map = RequestMap()
    request_map.bind(JoinMeetingRoomCommand, JoinMeetingRoomCommandHandler)
    container = configure_di()

    redis_client = redis.Redis.from_url("redis://localhost:6379/0")

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
