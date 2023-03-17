from redis import asyncio as redis

from dataclasses import dataclass
from rodi import Container, ServiceLifeStyle
from diator.middlewares import BaseMiddleware
from diator.events.message_brokers.redis import RedisMessageBroker
from diator.events import EventEmitter, EventMap
from diator.mediator import Mediator
from diator.container.rodi import RodiContainer
from diator.requests import Request, RequestHandler, RequestMap
from diator.response import Response


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


class TestMiddleware(BaseMiddleware):
    _counter = 0

    async def process_request(self, request: Request) -> None:
        self._counter += 5

    async def process_response(self, response: Response) -> None:
        ...


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
    middleware = TestMiddleware()

    event_emitter = EventEmitter(
        message_broker=RedisMessageBroker(redis_client),
        event_map=EventMap(),
        container=rodi_container,
    )

    mediator = Mediator(
        request_map=request_map,
        event_emitter=event_emitter,
        container=rodi_container,
        middlewares=[middleware],
    )

    await mediator.send(JoinMeetingRoomCommand(user_id=1, meeting_id=1))

    value = await redis_client.get("1")

    assert value == b"1"
