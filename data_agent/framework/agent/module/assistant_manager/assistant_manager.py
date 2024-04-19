from abc import abstractmethod

from data_agent.framework.agent.context import Context
from data_agent.framework.agent.module.assistant_manager.assistant.assistant import (
    Assistant,
)
from data_agent.framework.agent.module.loader import Loader
from data_agent.framework.module.keys import Keys


class AssistantManager(Loader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        llm_dic = self.init_assistant()
        for key, value in llm_dic.items():
            super().load(key, value)

    @abstractmethod
    def init_assistant(self) -> dict[Keys, type[Assistant]]:
        pass

    def get_assistant(self, key: Keys) -> type[Assistant]:
        return super().get_lazy(key, Assistant)
