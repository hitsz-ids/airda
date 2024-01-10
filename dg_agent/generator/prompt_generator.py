import json
import os
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings

from dg_agent.db.models.types import (
    TableDescription,
    ColumnDetail,
    ForeignKeyDetail
)
from dg_agent.generator.redis_client import Redis

load_dotenv()
embeddings_model_name = os.environ.get('EMBEDDINGS_MODEL_NAME')
redis_uri = os.environ.get('REDIS_URI')
redis_port = os.environ.get('REDIS_PORT')
redis_pwd = os.environ.get('REDIS_PWD')
redis_client = Redis(redis_uri,redis_port,redis_pwd)
TABLE_PREFIX = 'tableSchemaDetails-'
PROMPT = """
system: 你是一个出色的SQL专家。
不要使用"IN"、"OR"、"LEFT JOIN"、"INNER JOIN"，因为它们可能导致额外的结果，可以使用"INTERSECT"或"EXCEPT"代替，当必要时记得使用"DISTINCT"或"LIMIT"。
user:
"""
TABLE_SCHEMAS = """
根据数据库描述信息:
{table_schemas}
"""
SQL_TYPE = """
请使用有效的{sql_type}语法,
"""
COLUMN_INFO = """
结合数据库描述信息:
{description_info}
"""
FEWSHOT_EXAMPLE = """
结合fewshot示例：
{fewshot_example}
"""
KNOWNLEDGE_INFO = """
结合知识库信息：
{context}
"""
SQL_GENERATOR_STR = """
编写正确的SQL代码,并给出解释
"""
QUESTION_STR = """
回答下面的问题：{question}
"""

KNOWLEDGE_PROMPT = """
system:你是一个出色的数据分析师，我会给你一些示例，你可以参考这些示例，帮我查找并返回需要的数据。
请结合已知内容,回答所提出的问题.
user:
"""


def json_to_table(table_json) -> TableDescription:
    id = table_json['id']
    db_connection_id = table_json['db_connection_id']
    table_name = table_json['table_name']
    description = table_json['description']
    table_schema = table_json['table_schema']
    last_schema_sync = table_json['last_schema_sync']
    date_format = "%Y-%m-%d %H:%M:%S"
    try:
        last_schema_sync = datetime.strptime(last_schema_sync, date_format)
    except:
        last_schema_sync = None
    status = table_json['status']
    error_message = table_json['error_message']
    examples = table_json['examples']
    return TableDescription(
        id=id,
        db_connection_id=db_connection_id,
        table_name=table_name,
        description=description,
        table_schema=table_schema,
        last_schema_sync=last_schema_sync,
        status=status,
        error_message=error_message,
        examples=examples
    )


def get_embedding(
        text: str,
        model: str = "text-embedding-ada-002"
) -> List[float]:
    text = text.replace("\n", " ")
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    return embeddings.embed_query(text)


def json_to_column(column_json) -> ColumnDetail:
    foreign_key_data = column_json["foreign_key"]
    foreign_key = None
    if foreign_key_data:
        foreign_key = ForeignKeyDetail(
            field_name=foreign_key_data['foreign_key_data'],
            reference_table=foreign_key_data['reference_table']
        )
    is_primary_key = column_json['is_primary_key']
    if not is_primary_key:
        is_primary_key = False
    return ColumnDetail(
        name=column_json['name'],
        is_primary_key=is_primary_key,
        data_type=column_json['data_type'],
        description=column_json['description'],
        low_cardinality=column_json['low_cardinality'],
        categories=column_json['categories'],
        foreign_key=foreign_key
    )


def get_all_tables(db_connection_id) -> List[TableDescription]:
    json_data = redis_client.get(TABLE_PREFIX + str(db_connection_id))
    tables = []
    if json_data:
        data = json.loads(json_data)
        for item in data:
            table = json_to_table(item)
            fields_data = item['columns']
            columns = []
            for field in fields_data:
                column = json_to_column(field)
                columns.append(column)
            table.columns = columns
            tables.append(table)
    return tables


def cosine_similarity(a: List[float], b: List[float]) -> float:
    return round(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), 4)


def get_similarity_table_names(question: str, tables: List[TableDescription]) -> List[str]:
    question_embedding = get_embedding(question)
    table_representations = []
    for table in tables:
        col_rep = ""
        for column in table.columns:
            col_rep += column.name + " "
        table_rep = f"Table {table.table_name} contain columns: {col_rep}, this tables has: {table.description}"
        table_representations.append([table.table_name, table_rep])
    df = pd.DataFrame(
        table_representations, columns=["table_name", "table_representation"]
    )
    df["table_embedding"] = df.table_representation.apply(
        lambda x: get_embedding(x)
    )
    df["similarities"] = df.table_embedding.apply(
        lambda x: cosine_similarity(x, question_embedding)
    )
    df = df.sort_values(by='similarities', ascending=False)
    print('所有表的相似度:\n')
    for index, row in df.iterrows():
        table = f'Table: {row["table_name"]}, relevance score: {row["similarities"]}\n'
        print(table)
    # 根据相似度选数据
    condition = df['similarities'] >= 0.65
    result = df[condition]
    print('筛选相似度后:\n')
    for index, row in result.iterrows():
        table = f'Table: {row["table_name"]}, relevance score: {row["similarities"]}\n'
        print(table)
    # 如果条件未满足，取前5行
    if len(result) <= 10:
        result = df.head(10)

    # table_relevance = ""
    # for _, row in result:
    #     table_relevance += (
    #         f'Table: {row["table_name"]}, relevance score: {row["similarities"]}\n'
    #     )
    similarity_tables = result['table_name'].values
    return similarity_tables


def get_similarity_tables(question: str, db_connection_id: str):
    all_tables = get_all_tables(db_connection_id)
    similarity_table_names = get_similarity_table_names(question, all_tables)
    similarity_tables = []
    for table in all_tables:
        if table.table_name in similarity_table_names:
            similarity_tables.append(table)
    return similarity_tables


def get_table_schemas(tables: List[TableDescription]) -> str:
    tables_schema = ""
    for table in tables:
        tables_schema += table.table_schema + "\n"
        if table.description is not None:
            tables_schema += "Table description: " + table.description + "\n"
    return tables_schema


def get_column_info(tables: List[TableDescription]) -> str:
    column_full_info = ""
    for table in tables:
        table_name = table.table_name

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
            column_full_info += f"Table: {table_name}, column: {column_name}, additional info: {col_info}\n"
    return column_full_info


def generate_sql_prompt(question: str,
                        db_connection_id: str,
                        sql_type: str,
                        fewshot_example: str,
                        knowledge: str) -> str:
    similarity_tables = get_similarity_tables(question, db_connection_id)
    table_schemas = get_table_schemas(similarity_tables)
    # column_info = get_column_info(similarity_tables)
    prompt = PROMPT
    prompt += SQL_TYPE.format(sql_type=sql_type)
    if table_schemas:
        prompt += TABLE_SCHEMAS.format(table_schemas=table_schemas)
    # if column_info:
    #     prompt += COLUMN_INFO.format(description_info=column_info)
    if fewshot_example:
        prompt += FEWSHOT_EXAMPLE.format(fewshot_example=fewshot_example)
    if knowledge:
        prompt += KNOWNLEDGE_INFO.format(context=knowledge)
    prompt += SQL_GENERATOR_STR
    prompt += QUESTION_STR.format(question=question)
    return prompt


def generate_knowledge_prompt(question: str, db_connection_id: str, knowledge: str):
    similarity_tables = get_similarity_tables(question, db_connection_id)
    table_schemas = get_table_schemas(similarity_tables)
    prompt = KNOWLEDGE_PROMPT
    print("table_schemas", table_schemas)
    if table_schemas:
        prompt += TABLE_SCHEMAS.format(table_schemas=table_schemas)
    # column_info = get_column_info(similarity_tables)
    # if column_info:
    #     prompt += COLUMN_INFO.format(description_info=column_info)
    if knowledge:
        prompt += KNOWNLEDGE_INFO.format(context=knowledge)
    prompt += QUESTION_STR.format(question=question)
    return prompt
