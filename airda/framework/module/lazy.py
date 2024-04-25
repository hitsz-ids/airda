from abc import ABC

from airda.framework.module.dynamic import DynamicModule


class Lazy(DynamicModule, ABC):
    def __init__(self):
        super().__init__()

    def ready(self):
        pass

    def create(self):
        pass

    def resume(self):
        pass

    def destroy(self):
        pass


class LazyContext:
    pass
