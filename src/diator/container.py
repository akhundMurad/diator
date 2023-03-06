from typing import Protocol, Type, TypeVar

T = TypeVar("T")


class Container(Protocol):
    """
    The interface of container-like objects (implemented by di, rodi libraries).

    If di-framework doesn't support this interface, abstraction over it should be defined.
    """

    def get(self, instance_type: Type[T]) -> T:
        ...
