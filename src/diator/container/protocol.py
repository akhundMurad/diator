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

    @external_container.setter
    def external_container(self, external_container: C) -> None:
        ...

    async def resolve(self, type_: Type[T]) -> T:
        ...
