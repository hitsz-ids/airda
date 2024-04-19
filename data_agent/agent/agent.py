from overrides import overrides

from data_agent.agent import log
from data_agent.agent.assistants.assistant_manager import DataAgentAssistantManager
from data_agent.agent.data_agent_context import DataAgentContext
from data_agent.agent.llm.data_agent_llm_manager import DataAgentLLMManager
from data_agent.agent.planner.data_agent_planner import DataAgentPlanner
from data_agent.framework.agent.agent import Agent
from data_agent.framework.agent.module.assistant_manager.assistant_manager import (
    AssistantManager,
)
from data_agent.framework.agent.module.llm_manager.llm_manager import LLMManager
from data_agent.framework.agent.module.planner.planner import Planner

logger = log.getLogger()


class DataAgent(Agent[DataAgentContext]):
    def __init__(self):
        super().__init__()
        self.context.load_rag()
        self.context.load_storage()

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
