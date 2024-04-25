from airda.agent.assistants.assistant_keys import AssistantKeys
from airda.agent.assistants.chat_assistant.chat_assistant import ChatAssistant
from airda.agent.assistants.sql_assistant.sql_assistant import SqlAssistant
from airda.framework.agent.module.assistant_manager.assistant.assistant import (
    Assistant,
)
from airda.framework.agent.module.assistant_manager.assistant_manager import (
    AssistantManager,
)
from airda.framework.module.keys import Keys


class DataAgentAssistantManager(AssistantManager):
    def init_assistant(self) -> dict[Keys, type[Assistant]]:
        return {
            AssistantKeys.SQL_ASSISTANT: SqlAssistant,
            AssistantKeys.CHAT_ASSISTANT: ChatAssistant,
        }
