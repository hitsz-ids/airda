from airda.agent.llm.data_agent_llm_keys import DataAgentLLMKeys
from airda.agent.llm.openai import OpenAILLM
from airda.framework.agent.module.llm_manager.llm.llm import LLM
from airda.framework.agent.module.llm_manager.llm_manager import LLMManager


class DataAgentLLMManager(LLMManager):
    def init_llm(self) -> dict[DataAgentLLMKeys, type[LLM]]:
        return {DataAgentLLMKeys.ChatLLM: OpenAILLM, DataAgentLLMKeys.SqlLLM: OpenAILLM}
