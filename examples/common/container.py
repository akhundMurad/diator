from typing import TypeVar, Type


T = TypeVar("T")


class Container:
    def get(self, instance_type: Type[T]) -> T:
        return instance_type()
