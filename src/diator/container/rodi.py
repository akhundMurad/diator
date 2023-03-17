from typing import Type, TypeVar

try:
    from rodi import Container as ExternalContainer  # type: ignore
except ImportError:

    class ExternalContainer:  # type: ignore
        def __init__(self) -> None:
            raise ImportError("Rodi is required to use this module")


from diator.container.protocol import Container

T = TypeVar("T")


class RodiContainer(Container[ExternalContainer]):
    def __init__(self) -> None:
        self._external_container: ExternalContainer | None = None

    @property
    def external_container(self) -> ExternalContainer:
        if not self._external_container:
            raise AttributeError

        return self._external_container

    def attach_external_container(self, container: ExternalContainer) -> None:
        self._external_container = container

    async def resolve(self, type_: Type[T]) -> T:
        if hasattr(self.external_container, "resolve"):
            return self.external_container.resolve(type_)
        return self._build_by_provider(type_)

    def _build_by_provider(self, type_: Type[T]) -> T:
        services = self.external_container.build_provider()
        return services.get(type_)
