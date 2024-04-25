from abc import ABC, abstractmethod

from airda.agent.env import DataAgentEnv
from airda.agent.llm.openai import OpenAILLM
from airda.framework.agent.context import Context
from airda.framework.agent.module.llm_manager.llm.llm import LLM
from airda.framework.agent.module.loader import Loader
from airda.framework.module.keys import Keys


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
