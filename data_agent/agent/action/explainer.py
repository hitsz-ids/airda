import json
from typing import TYPE_CHECKING, AsyncGenerator, Optional

from overrides import overrides
from pydantic import BaseModel

from data_agent.agent.action.searcher import SearcherResult
from data_agent.agent.action.sql_generator import SQLGeneratorResult
from data_agent.framework.action.action_params import ActionParams
from data_agent.framework.action.action_result import ActionResult
from data_agent.framework.action.llm_action import LLMAction

if TYPE_CHECKING:
    from data_agent.framework.agent.context import Context

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


class ExplainerParams(ActionParams, BaseModel):
    question: str
    generator_result: Optional[SQLGeneratorResult] = None
    searcher_result: Optional[SearcherResult] = None


class ExplainerResult(ActionResult, BaseModel):
    session_token: str
    token: str


class Explainer(LLMAction[ExplainerParams, ExplainerResult]):
    @overrides
    def init_name(self) -> str:
        return "Explainer"

    @overrides
    async def execute(self, context: "Context") -> AsyncGenerator[ExplainerResult, None]:
        message = self.make_message()
        result = ExplainerResult(session_token="", token="")
        async for chunk in self.llm_api.chat_completion_stream(messages=[message]):
            json_line = chunk[6:]
            if json_line.strip() == "[DONE]":
                result.session_token = "[DONE]"
            else:
                data = json.loads(json_line)
                session_token = data["choices"][0]["delta"].get("content", "")
                result.session_token = session_token
            result.token += result.session_token
            yield result

    @overrides
    def init_prompt(self) -> str:
        question = self.params.question
        prompt = SQL_ASSISTANT
        sql = ""
        # sql生成是否有结果
        if self.params.generator_result is not None:
            sql = self.params.generator_result.sql
        # 找数是否有结果
        if self.params.searcher_result is not None:
            table_schema = self.params.searcher_result.tables_schema
            if table_schema:
                prompt += TABLE_SCHEMA_PROMPT.format(schema=table_schema)
        prompt += SQL_EXPLAIN_QUESTION.format(question=question, sql=sql)
        return prompt
