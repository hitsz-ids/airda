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
