from sql_agent.framework.assistant.action.llm_action import LlmAction
from sql_agent.protocol import ChatCompletionRequest

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


class Generator(LlmAction):
    def init_name(self):
        return "生成sql"

    def execute(self):
        self._result = "Generator"

    def init_prompt(self, request: ChatCompletionRequest):
        (table_schema, knowledge, question, sql_type, few_shot_example) = request
        sql_type = sql_type or "mysql"
        prompt = SQL_ASSISTANT
        if table_schema:
            prompt += TABLE_SCHEMA_PROMPT.format(schema=table_schema)
        prompt += SQL_TYPE.format(sql_type)
        if knowledge:
            prompt += KNOWLEDGE_INFO.format(context=knowledge)
        if few_shot_example:
            prompt += FEW_SHOT_EXAMPLE.format(few_shot_example)
        prompt += SQL_GENERATOR_QUESTION.format(question=question)
        return prompt
