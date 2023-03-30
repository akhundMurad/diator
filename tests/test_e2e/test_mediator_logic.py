from dataclasses import dataclass

from redis import asyncio as redis
from rodi import Container, ServiceLifeStyle

from diator.container.rodi import RodiContainer
from diator.events import EventEmitter, EventMap
from diator.events.message_brokers.redis import RedisMessageBroker
from diator.mediator import Mediator
from diator.middlewares import MiddlewareChain
from diator.requests import Request, RequestHandler, RequestMap


@dataclass(frozen=True, kw_only=True)
class JoinMeetingRoomCommand(Request):
    meeting_id: int
    user_id: int


class JoinMeetingRoomCommandHandler(RequestHandler[JoinMeetingRoomCommand, None]):
    def __init__(self, redis_client: redis.Redis) -> None:
        self._events = []
        self._redis_client = redis_client

    @property
    def events(self) -> list:
        return self._events

    async def handle(self, request: JoinMeetingRoomCommand) -> None:
        await self._redis_client.set(str(request.meeting_id), str(request.user_id))


class TestMiddleware:
    _counter = 0

    async def __call__(self, request: Request, handle):
        self._counter += 5
        return await handle(request)


async def test_send_command_with_middleware(redis_client: redis.Redis):
    container = Container()
    container.register_factory(
        lambda: redis.Redis.from_url("redis://localhost:6379/0"),
        redis.Redis,
        ServiceLifeStyle.TRANSIENT,
    )
    container.register(JoinMeetingRoomCommandHandler)
    rodi_container = RodiContainer()
    rodi_container.attach_external_container(container)

    request_map = RequestMap()
    request_map.bind(JoinMeetingRoomCommand, JoinMeetingRoomCommandHandler)

    redis_client = redis.Redis.from_url("redis://localhost:6379/0")
    middleware_chain = MiddlewareChain()
    middleware_chain.add(TestMiddleware())

    event_emitter = EventEmitter(
        message_broker=RedisMessageBroker(redis_client),
        event_map=EventMap(),
        container=rodi_container,
    )

    mediator = Mediator(
        request_map=request_map,
        event_emitter=event_emitter,
        container=rodi_container,
        middleware_chain=middleware_chain,
    )

    await mediator.send(JoinMeetingRoomCommand(user_id=1, meeting_id=1))

    value = await redis_client.get("1")

    assert value == b"1"
