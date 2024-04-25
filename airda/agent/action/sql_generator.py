from typing import TYPE_CHECKING, AsyncGenerator, Optional

from overrides import overrides
from pydantic import BaseModel

from airda.agent import log
from airda.agent.action.searcher import SearcherResult
from airda.framework.action.action_params import ActionParams
from airda.framework.action.action_result import ActionResult
from airda.framework.action.llm_action import LLMAction

if TYPE_CHECKING:
    from airda.framework.agent.context import Context
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

logger = log.getPromptLogger()


class SQLGeneratorParams(BaseModel, ActionParams):
    question: str
    searcher_result: Optional[SearcherResult] = None


class SQLGeneratorResult(BaseModel, ActionResult):
    sql: str = None


class SqlGenerator(LLMAction[SQLGeneratorParams, SQLGeneratorResult]):
    @overrides
    def init_name(self) -> str:
        return "SqlGenerator"

    @overrides
    async def execute(self, context: "Context") -> AsyncGenerator[SQLGeneratorResult, None]:
        logger.info(self.prompt)
        message = self.make_message()
        model_output = self.llm_api.chat_completion(messages=[message])
        result = SQLGeneratorResult()
        sql = model_output["choices"][0]["message"]["content"]
        if not sql.startswith("```sql"):
            sql = f"```sql\n {sql} \n```\n"
        else:
            sql += "\n"
        result.sql = sql
        yield result

    @overrides
    def init_prompt(self) -> str:
        question = self.params.question
        sql_type = self.params.searcher_result.kind
        table_schema = None
        knowledge = None
        few_shot_example = None
        if self.params.searcher_result is not None:
            table_schema = self.params.searcher_result.tables_schema
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
