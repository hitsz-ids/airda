from abc import ABC

from data_agent.framework.module.dynamic import DynamicModule


class Immediate(DynamicModule, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self):
        pass

    def resume(self):
        pass

    def destroy(self):
        pass
