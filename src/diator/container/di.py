from typing import Type, TypeVar

import di
from di.dependent import Dependent
from di.executors import AsyncExecutor

from diator.container.protocol import Container

T = TypeVar("T")


class DIContainer(Container[di.Container]):
    def __init__(self) -> None:
        self._external_container: di.Container | None = None

    @property
    def external_container(self) -> di.Container:
        if not self._external_container:
            raise AttributeError

        return self._external_container

    def attach_external_container(self, container: di.Container) -> None:
        self._external_container = container

    async def resolve(self, type_: Type[T]) -> T:
        executor = AsyncExecutor()
        solved = self.external_container.solve(Dependent(type_, scope="request"), scopes=["request"])
        with self.external_container.enter_scope("request") as state:
            return await solved.execute_async(executor=executor, state=state)
