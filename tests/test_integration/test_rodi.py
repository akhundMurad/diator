from rodi import Container

from diator.container.rodi import RodiContainer


class Dependency:
    ...


async def test_rodi_container_resolve() -> None:
    external_container = Container()

    external_container.register(Dependency)

    rodi_container = RodiContainer()
    rodi_container.attach_external_container(external_container)

    resolved = await rodi_container.resolve(Dependency)

    assert isinstance(resolved, Dependency)
