from typing import Type, TypeVar

import rodi

from diator.container.protocol import Container

T = TypeVar("T")


class RodiContainer(Container[rodi.Container]):
    def __init__(self) -> None:
        self._external_container: rodi.Container | None = None

    @property
    def external_container(self) -> rodi.Container:
        if not self._external_container:
            raise AttributeError

        return self._external_container

    def attach_external_container(self, container: rodi.Container) -> None:
        self._external_container = container

    async def resolve(self, type_: Type[T]) -> T:
        if hasattr(self.external_container, "resolve"):
            return self.external_container.resolve(type_)
        return self._build_by_provider(type_)

    def _build_by_provider(self, type_: Type[T]) -> T:
        services = self.external_container.build_provider()
        return services.get(type_)
