from abc import abstractmethod
from typing import Generic, TypeVar

from airda.framework.agent.context import Context
from airda.framework.agent.module.assistant_manager.assistant_manager import (
    AssistantManager,
)
from airda.framework.agent.module.llm_manager.llm_manager import LLMManager
from airda.framework.agent.module.planner.planner import Planner

C = TypeVar("C", bound=Context)


class Agent(Generic[C]):
    context: C

    def __init__(self):
        self.context = self.init_context()
        self.context.load_planner(self.init_planner())
        self.context.load_llm(self.init_llm_manager())
        self.context.load_assistant(self.init_assistant_manager())

    def run(self) -> C:
        return self.context

    @abstractmethod
    def init_context(self) -> C:
        pass

    @abstractmethod
    def init_planner(self) -> type[Planner]:
        pass

    @abstractmethod
    def init_llm_manager(self) -> type[LLMManager]:
        pass

    @abstractmethod
    def init_assistant_manager(self) -> type[AssistantManager]:
        pass
