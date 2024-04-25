from abc import ABC, abstractmethod

from aida.agent.env import DataAgentEnv
from aida.agent.llm.openai import OpenAILLM
from aida.framework.agent.context import Context
from aida.framework.agent.module.llm_manager.llm.llm import LLM
from aida.framework.agent.module.loader import Loader
from aida.framework.module.keys import Keys


class LLMManager(Loader, ABC):
    context: Context = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        llm_dic = self.init_llm()
        for key, value in llm_dic.items():
            super().load(key, value)

    @abstractmethod
    def init_llm(self) -> dict[Keys, type[LLM]]:
        pass

    def get_llm(self, key: Keys) -> LLM:
        llm_type = super().get_lazy(key, LLM)
        if llm_type == OpenAILLM:
            llm = OpenAILLM(key=DataAgentEnv().get("openai_api_key"))
        else:
            llm = llm_type()
        return llm
