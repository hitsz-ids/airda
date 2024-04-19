from data_agent.agent.assistants.assistant_keys import AssistantKeys
from data_agent.agent.assistants.chat_assistant.chat_assistant import ChatAssistant
from data_agent.agent.assistants.sql_assistant.sql_assistant import SqlAssistant
from data_agent.framework.agent.module.assistant_manager.assistant.assistant import (
    Assistant,
)
from data_agent.framework.agent.module.assistant_manager.assistant_manager import (
    AssistantManager,
)
from data_agent.framework.module.keys import Keys


class DataAgentAssistantManager(AssistantManager):
    def init_assistant(self) -> dict[Keys, type[Assistant]]:
        return {
            AssistantKeys.SQL_ASSISTANT: SqlAssistant,
            AssistantKeys.CHAT_ASSISTANT: ChatAssistant,
        }
