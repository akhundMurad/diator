import functools
from typing import Awaitable, Callable, Protocol, TypeVar

from diator.requests import Request
from diator.response import Response

Req = TypeVar("Req", bound=Request, contravariant=True)
Res = TypeVar("Res", Response, None, covariant=True)
HandleType = Callable[[Req], Awaitable[Res]]


class Middleware(Protocol):
    async def __call__(self, request: Request, handle: HandleType) -> Res:
        ...


Handle = Callable[[Req], Awaitable[Res]]


class MiddlewareChain:
    def __init__(self) -> None:
        self._chain: list[Middleware] = []

    def set(self, chain: list[Middleware]) -> None:
        self._chain = chain

    def add(self, middleware: Middleware) -> None:
        self._chain.append(middleware)

    def wrap(self, handle: Handle) -> Handle:
        for middleware in reversed(self._chain):
            handle = functools.partial(middleware.__call__, handle=handle)

        return handle
