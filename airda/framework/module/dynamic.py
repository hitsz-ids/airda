from abc import ABC, abstractmethod

from airda.framework.obj.object import Object


class DynamicModule(ABC, Object):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def destroy(self):
        pass
