import logging
from typing import Awaitable, Callable, Mapping, Protocol, TypeVar

from diator.requests import Request
from diator.response import Response

Req = TypeVar("Req", bound=Request, contravariant=True)
Res = TypeVar("Res", Response, None, covariant=True)
HandleType = Callable[[Req], Awaitable[Res]]


class Logger(Protocol):
    def log(self, level: int, msg: str, *args, extra: Mapping[str, object] | None = None) -> None:  # noqa
        ...


class LoggingMiddleware:
    def __init__(
        self,
        logger: Logger | None = None,
        level: int = logging.DEBUG,
    ) -> None:
        self._logger = logger or logging.getLogger(__name__)
        self._level = level

    async def __call__(self, request: Request, handle: HandleType) -> Res:
        self._logger.log(
            self._level,
            "Handle %s request",
            type(request).__name__,
            extra={"request": request},
        )
        response = await handle(request)
        self._logger.log(
            self._level,
            "Request %s handled. Response: %s",
            type(request).__name__,
            response,
            extra={"request": request},
        )

        return response
