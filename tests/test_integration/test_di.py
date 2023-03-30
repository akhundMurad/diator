from di import Container, bind_by_type
from di.dependent import Dependent

from diator.container.di import DIContainer


class Dependency:
    ...


async def test_rodi_container_resolve() -> None:
    external_container = Container()

    external_container.bind(
        bind_by_type(Dependent(Dependency, scope="request"), Dependency)
    )

    di_container = DIContainer()
    di_container.attach_external_container(external_container)

    resolved = await di_container.resolve(Dependency)

    assert isinstance(resolved, Dependency)
