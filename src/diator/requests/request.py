from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class Request:
    request_id: UUID = field(default_factory=uuid4)
