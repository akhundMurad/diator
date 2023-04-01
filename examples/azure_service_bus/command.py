from dataclasses import dataclass
from datetime import timedelta

from diator.requests import Request


@dataclass(frozen=True, kw_only=True)
class CleanUnactiveUsersCommand(Request):
    eta: timedelta
