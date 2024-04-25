from aida.agent.assistants.assistant_keys import AssistantKeys
from aida.agent.assistants.chat_assistant.chat_assistant import ChatAssistant
from aida.agent.assistants.sql_assistant.sql_assistant import SqlAssistant
from aida.framework.agent.module.assistant_manager.assistant.assistant import (
    Assistant,
)
from aida.framework.agent.module.assistant_manager.assistant_manager import (
    AssistantManager,
)
from aida.framework.module.keys import Keys


class DataAgentAssistantManager(AssistantManager):
    def init_assistant(self) -> dict[Keys, type[Assistant]]:
        return {
            AssistantKeys.SQL_ASSISTANT: SqlAssistant,
            AssistantKeys.CHAT_ASSISTANT: ChatAssistant,
        }
