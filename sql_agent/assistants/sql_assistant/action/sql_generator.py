from typing import AsyncGenerator

from overrides import overrides

from sql_agent.framework.assistant.action import ActionResult
from sql_agent.framework.assistant.action.llm_action import LlmAction
from sql_agent.llm import SQLLLM
from sql_agent.llm.openai import OpenAILLM
from sql_agent.protocol import ChatCompletionRequest
from sql_agent.setting import System

SQL_ASSISTANT = """
你是一个世界级SQL专家
"""

TABLE_SCHEMA_PROMPT = """
请根据以下建表语句中的表名和字段名及其备注信息:
{schema}
"""

SQL_TYPE = """
请使用有效的{sql_type}语法,
"""

SQL_GENERATOR_QUESTION = """
生成以下查询问题的SQL语句：
{question}
请确保：
1.不用对结果进行解释
2.只输出生成的SQL
"""

KNOWLEDGE_INFO = """
利用知识库信息：
{context}
"""

FEW_SHOT_EXAMPLE = """
结合以下示例：
{few_shot_example}
"""

system = System()


class SQLGenerator(LlmAction):
    def __init__(self, request: ChatCompletionRequest, action_results: dict[str, dict]):
        super().__init__(request, action_results)
        self.llm_api = system.get_module(SQLLLM)

    def init_name(self):
        return "SQLGenerator"

    @overrides
    async def execute(self) -> AsyncGenerator[str, None]:
        message = self.make_message()
        model_output = await self.llm_api.chat_completion(messages=[message])
        sql = model_output["choices"][0]["message"]["content"]
        self.set_result({"sql": sql})
        if not sql.startswith("```sql"):
            sql = f"```sql\n {sql} \n```"
        else:
            sql += "\n"
        yield sql

    def init_prompt(self):
        question = self._request.question
        sql_type = self._request.sql_type
        searcher_param = self._actions_results.get("Searcher")
        table_schema = searcher_param.get("table_schema")
        knowledge = searcher_param.get("knowledge")
        few_shot_example = searcher_param.get("few_shot_example")
        prompt = SQL_ASSISTANT

        if table_schema:
            prompt += TABLE_SCHEMA_PROMPT.format(schema=table_schema)
        prompt += SQL_TYPE.format(sql_type=sql_type)
        if knowledge:
            prompt += KNOWLEDGE_INFO.format(context=knowledge)
        if few_shot_example:
            prompt += FEW_SHOT_EXAMPLE.format(few_shot_example=few_shot_example)
        prompt += SQL_GENERATOR_QUESTION.format(question=question)
        return prompt
