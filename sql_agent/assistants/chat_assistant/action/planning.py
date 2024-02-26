from sql_agent.framework.assistant.action.llm_action import LlmAction


class Planning(LlmAction):

    def init_prompt(self, _question) -> str:
        pass

    def execute(self) -> bool:
        """
        调用chat的大模型，进行规划输出
        """
        pass