import functools
from typing import Protocol, TypeVar, Callable, Awaitable
from diator.requests.request import Request

from diator.requests.request_handler import RequestHandler
from diator.response import Response


Req = TypeVar("Req", bound=Request, contravariant=True)
Res = TypeVar("Res", Response, None, covariant=True)
HandleType = Callable[[Req], Awaitable[Res]]


class Middleware(Protocol):
    async def __call__(self, request: Request, handle: HandleType) -> Res:
        ...


class MiddlewareChain:
    def __init__(self) -> None:
        self._chain: list[Middleware] = []

    def set(self, chain: list[Middleware]) -> None:
        self._chain = chain

    def add(self, middleware: Middleware) -> None:
        self._chain.append(middleware)

    def wrap(self, handler: RequestHandler[Req, Res]) -> RequestHandler[Req, Res]:
        handle = handler.handle

        for middleware in reversed(self._chain):
            handle = functools.partial(middleware.__call__, handle=handle)  # type: ignore

        handler.handle = handle  # type: ignore

        return handler
