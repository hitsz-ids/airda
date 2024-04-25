from typing import TypeVar, cast

C = TypeVar("C", bound="Convert")


class Object:
    def convert(self, cls: type[C]) -> C:
        if isinstance(self, cls):
            return cast(C, self)
        raise TypeError(f"Cannot convert {cls} into {cls}")
