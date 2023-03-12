from typing import Type, TypeVar

from di.executors import AsyncExecutor
from di.dependent import Dependent
from di import ScopeState
from di import Container as ExternalContainer

from diator.container.protocol import Container

T = TypeVar("T")


class DIContainer(Container[ExternalContainer]):
    def __init__(self, async_executor: AsyncExecutor) -> None:
        self._async_executor = async_executor
        self._external_container: ExternalContainer | None = None
        self._scope: ScopeState | None = None

    @property
    def external_container(self) -> ExternalContainer:
        if not self._external_container:
            raise AttributeError

        return self._external_container

    @external_container.setter
    def external_container(self, external_container: ExternalContainer) -> None:
        self._external_container = external_container

    async def resolve(self, type_: Type[T]) -> T:
        executor = AsyncExecutor()
        solved = self.external_container.solve(
            Dependent(type_, scope="request"), scopes=["request"]
        )
        solved.dependency
        with self.external_container.enter_scope("request") as state:
            return await solved.execute_async(executor=executor, state=state)
