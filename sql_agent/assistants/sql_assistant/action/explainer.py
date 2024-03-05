from sql_agent.framework.assistant.action.llm_action import LlmAction

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
    prompt = """请帮哦我解释生成的结果"""

    def init_name(self):
        return "Explainer"

    def execute(self):
        self._result = "Explainer"

    def init_prompt(self, param: dict):
        (table_schema, knowledge, question, sql) = param
        prompt = SQL_ASSISTANT
        if table_schema:
            prompt += TABLE_SCHEMA_PROMPT.format(schema=table_schema)
        if knowledge:
            prompt += KNOWLEDGE_INFO.format(context=knowledge)
        prompt += SQL_EXPLAIN_QUESTION.format(question=question, sql=sql)
        return prompt
