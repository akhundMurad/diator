from typing import Protocol, Type, TypeVar


T = TypeVar("T")


class Container(Protocol):
    def get(self, instance_type: Type[T]) -> T:
        ...
