# Dependency Injection

Dependency Injection pattern (DI) separates the concerns of constructing objects and using them, leading to loosely coupled programs.

## Usage in Diator

In Diator, dependency injection is implemented via special `Container` class, which is literally an abstraction over various dependency injection frameworks. This allows developers to easily manage dependencies and decouple components, leading to more modular and maintainable code. Currently, Diator supports two popular DI-frameworks, [adriangb/di](https://github.com/adriangb/di) and [Neoteroi/rodi](https://github.com/Neoteroi/rodi), but we plan to expand support for other frameworks in the future.

## Neoteroi/rodi

Configure by 2 steps:

1. Setup dependencies:

    ```python
    from rodi import Container


    def configure_di():
        container = Container()

        container.register(UserJoinedEventHandler)
        container.register(JoinMeetingRoomCommandHandler)
    ```

2. Integrate with Diator:

    ```python hl_lines="3 12-13"
    from rodi import Container

    from diator.container.rodi import RodiContainer


    def configure_di() -> RodiContainer:
        container = Container()

        container.register(UserJoinedEventHandler)
        container.register(JoinMeetingRoomCommandHandler)

        rodi_container = RodiContainer()
        rodi_container.attach_external_container(container)

        return rodi_container
    ```

## adriangb/di

Configure by 2 steps:

1. Setup dependencies:

    ```python
    from di import Container, bind_by_type
    from di.dependent import Dependent


    def configure_di():
        container = Container()

        container.bind(bind_by_type(Dependent(UserJoinedEventHandler, scope="request"), UserJoinedEventHandler))
        container.bind(
            bind_by_type(
                Dependent(JoinMeetingRoomCommandHandler, scope="request"),
                JoinMeetingRoomCommandHandler,
            )
        )
    ```

2. Integrate with Diator:

    ```python hl_lines="4 18-19"
    from di import Container, bind_by_type
    from di.dependent import Dependent

    from diator.container.di import DIContainer


    def configure_di() -> DIContainer:
        container = Container()

        container.bind(bind_by_type(Dependent(UserJoinedEventHandler, scope="request"), UserJoinedEventHandler))
        container.bind(
            bind_by_type(
                Dependent(JoinMeetingRoomCommandHandler, scope="request"),
                JoinMeetingRoomCommandHandler,
            )
        )

        di_container = DIContainer()
        di_container.attach_external_container(container)

        return di_container
    ```

## Recources

- [Introduction IoC, DIP, DI and IoC Container](https://www.tutorialsteacher.com/ioc/introduction)

- [Dependency Injection Principles, Practices, and Patterns](https://www.oreilly.com/library/view/dependency-injection-principles/9781617294730/)

- [.NET dependency injection](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection)
