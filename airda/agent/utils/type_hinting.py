from typing import Generic, TypeVar

T = TypeVar("T")


class TypeHint(Generic[T]):
    _instance: T

    def __init__(self, instance: T):
        self._instance = instance

    def instance(self) -> T:
        return self._instance
