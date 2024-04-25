from overrides import overrides

from aida.agent import DataAgentKey, log
from aida.agent.assistants.assistant_manager import DataAgentAssistantManager
from aida.agent.data_agent_context import DataAgentContext
from aida.agent.llm.data_agent_llm_manager import DataAgentLLMManager
from aida.agent.planner.data_agent_planner import DataAgentPlanner
from aida.framework.agent.agent import Agent
from aida.framework.agent.module.assistant_manager.assistant_manager import (
    AssistantManager,
)
from aida.framework.agent.module.llm_manager.llm_manager import LLMManager
from aida.framework.agent.module.planner.planner import Planner

logger = log.getLogger()


class DataAgent(Agent[DataAgentContext]):
    def __init__(self, *args) -> None:
        super().__init__()
        if len(args) == 0:
            self.context.load_rag()
            self.context.load_storage()
        else:
            for item in args:
                if item == DataAgentKey.STORAGE:
                    self.context.load_storage()
                if item == DataAgentKey.RAG:
                    self.context.load_rag()

    def init_context(self) -> DataAgentContext:
        return DataAgentContext()

    @overrides
    def init_llm_manager(self) -> type[LLMManager]:
        return DataAgentLLMManager

    @overrides
    def init_assistant_manager(self) -> type[AssistantManager]:
        return DataAgentAssistantManager

    @overrides
    def init_planner(self) -> type[Planner]:
        return DataAgentPlanner
