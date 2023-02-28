from typing import TypeVar

from diator.events.event import Event
from diator.requests.request import Request
from diator.response import Response


E_contra = TypeVar("E_contra", bound=Event, contravariant=True)

Req_contra = TypeVar("Req_contra", bound=Request, contravariant=True)

Res_co = TypeVar("Res_co", Response, None, covariant=True)
