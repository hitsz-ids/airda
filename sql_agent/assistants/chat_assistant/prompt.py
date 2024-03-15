from typing import List

from sql_agent.db.repositories.types import TableDescription

PROMPT_OLD = """
system: 你是一个出色的SQL专家。
不要使用"IN"、"OR"、"LEFT JOIN"、"INNER JOIN"，因为它们可能导致额外的结果，可以使用"INTERSECT"或"EXCEPT"代替，当必要时记得使用"DISTINCT"或"LIMIT"。
user:
"""

SQL_ASSISTANT = """
你是一个世界级SQL专家
"""

# ----------component----------
TABLE_SCHEMA_PROMPT = """
请根据以下建表语句中的表名和字段名及其备注信息:
{schema}
"""

SQL_TYPE = """
请使用有效的{sql_type}语法,
"""

FEW_SHOT_EXAMPLE = """
结合以下示例：
{few_shot_example}
"""

KNOWLEDGE_INFO = """
利用知识库信息：
{context}
"""

KNOWLEDGE_PROMPT = """
请选出需要用到的表和字段并作出解释
"""

# ----------question----------
SQL_GENERATOR_QUESTION = """
生成以下查询问题的SQL语句：
{question}
请确保：
1.不用对结果进行解释
2.只输出生成的SQL
"""

SQL_EXPLAIN_QUESTION = """
要查询{question}。
请从整体含义和各部分关键字说明两部分，简要解释下列的SQL查询语句：
{sql}
"""

SEARCH_QUESTION = """
要查询{question}，请选出需要用到的表和字段并作出解释。
"""


def get_column_info(tables: List[TableDescription]) -> str:
    column_full_info = ""
    for table in tables:
        table_name = table.name

        for index, column in enumerate(table.columns):
            col_info = ""
            column_name = column.name
            col_info += f"Description: {column.description},"
            if column.low_cardinality:
                col_info += f" categories = {column.categories},"
            col_info += " Sample rows: "
            for row in table.examples:
                col_info += str(row[index]) + ", "
            col_info = col_info[:-2]
            column_full_info += (
                f"Table: {table_name}, column: {column_name}, additional info: {col_info}\n"
            )
    return column_full_info


def sql_prompt_old(
    question: str,
    sql_type: str,
    few_shot_example: str,
    knowledge: str,
    table_schemas: str,
) -> str:
    prompt = PROMPT_OLD
    prompt += SQL_TYPE.format(sql_type=sql_type)
    if table_schemas:
        prompt += TABLE_SCHEMA_PROMPT.format(schema=table_schemas)
    if few_shot_example:
        prompt += FEW_SHOT_EXAMPLE.format(few_shot_example=few_shot_example)
    if knowledge:
        prompt += KNOWLEDGE_INFO.format(context=knowledge)
    prompt += SQL_GENERATOR_QUESTION
    prompt += SEARCH_QUESTION.format(question=question)
    return prompt


def sql_prompt(
    question: str,
    knowledge: str,
    table_schema: str,
) -> str:
    prompt = SQL_ASSISTANT
    if table_schema:
        prompt += TABLE_SCHEMA_PROMPT.format(schema=table_schema)
    if knowledge:
        prompt += KNOWLEDGE_INFO.format(context=knowledge)
    prompt += SQL_GENERATOR_QUESTION.format(question=question)
    return prompt


def sql_explain_prompt(question: str, table_schema: str, knowledge: str, sql: str) -> str:
    prompt = SQL_ASSISTANT
    if table_schema:
        prompt += TABLE_SCHEMA_PROMPT.format(schema=table_schema)
    if knowledge:
        prompt += KNOWLEDGE_INFO.format(context=knowledge)
    prompt += SQL_EXPLAIN_QUESTION.format(question=question, sql=sql)
    return prompt


def search_prompt(question: str, knowledge: str, table_schemas: str):
    prompt = SQL_ASSISTANT
    if table_schemas:
        prompt += TABLE_SCHEMA_PROMPT.format(schema=table_schemas)
    if knowledge:
        prompt += KNOWLEDGE_INFO.format(context=knowledge)
    prompt += SEARCH_QUESTION.format(question=question)
    return prompt
