from typing import AsyncGenerator

from sql_agent.framework.assistant.action.llm_action import LlmAction


class Planning(LlmAction):

    def init_prompt(self) -> str:
        return ""

    def init_name(self) -> str:
        return "Planning"

    async def execute(self) -> AsyncGenerator[str, None]:
        """
        调用chat的大模型，进行规划输出
        """
        pass
