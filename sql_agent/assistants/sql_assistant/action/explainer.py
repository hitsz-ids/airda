import json
from typing import AsyncGenerator

from overrides import overrides

from sql_agent.framework.assistant.action import ActionResult, ActionResultScope
from sql_agent.framework.assistant.action.llm_action import LlmAction
from sql_agent.llm.openai import OpenAILLM
from sql_agent.protocol import ChatCompletionRequest

SQL_ASSISTANT = """
你是一个世界级SQL专家
"""

TABLE_SCHEMA_PROMPT = """
请根据以下建表语句中的表名和字段名及其备注信息:
{schema}
"""

KNOWLEDGE_INFO = """
利用知识库信息：
{context}
"""

SQL_EXPLAIN_QUESTION = """
要查询{question}。
请从整体含义和各部分关键字说明两部分，简要解释下列的SQL查询语句：
{sql}
"""


class Explainer(LlmAction):
    def __init__(self, request: ChatCompletionRequest, action_results: dict[str, dict]):
        super().__init__(request, action_results)
        self.llm_api = OpenAILLM()

    def init_name(self):
        return "Explainer"

    @overrides
    async def execute(self) -> AsyncGenerator[str, None]:
        message = self.make_message()
        async for chunk in self.llm_api.chat_completion_stream(messages=[message]):
            json_line = chunk[6:]
            if json_line.strip() == "[DONE]":
                yield "[DONE]"
            else:
                data = json.loads(json_line)
                token = data["choices"][0]["delta"].get("content", "")
                yield token

    def init_prompt(self):
        question = self._request.messages[0].content
        generator_result = self._actions_results.get("SQLGenerator")
        searcher_result = self._actions_results.get("Searcher")

        sql = generator_result.get("sql")

        table_schema = searcher_result.get("table_schema")
        knowledge = searcher_result.get("knowledge")
        prompt = SQL_ASSISTANT
        if table_schema:
            prompt += TABLE_SCHEMA_PROMPT.format(schema=table_schema)
        if knowledge:
            prompt += KNOWLEDGE_INFO.format(context=knowledge)
        prompt += SQL_EXPLAIN_QUESTION.format(question=question, sql=sql)
        return prompt
