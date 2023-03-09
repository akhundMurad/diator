from typing import Protocol, Type, TypeVar

T = TypeVar("T")
C = TypeVar("C")


class Container(Protocol[C]):
    """
    The container interface.
    """

    @property
    def external_container(self) -> C:
        ...

    def attach_external_container(self, container: C) -> None:
        ...

    async def resolve(self, type_: Type[T]) -> T:
        ...
