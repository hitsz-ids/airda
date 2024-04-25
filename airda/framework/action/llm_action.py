from abc import abstractmethod
from typing import Generic

from overrides import overrides

from airda.framework.action.action import P, R
from airda.framework.action.async_action import AsyncAction
from airda.framework.agent.module.llm_manager.llm.llm import LLM, ChatMessage


class LLMAction(Generic[P, R], AsyncAction[P, R]):
    prompt: str
    llm_api: LLM

    def __init__(self, params: P, llm: LLM):
        super().__init__(params)
        self.llm_api = llm
        self.prompt = self.init_prompt()

    @abstractmethod
    def init_prompt(self) -> str:
        pass

    def make_message(self, role: str = "user") -> ChatMessage:
        return {"role": role, "content": self.prompt}
