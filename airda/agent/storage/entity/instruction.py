from typing import Any

from pydantic import BaseModel

from airda.agent.storage.entity.colunm_detail import ColumnDetail


class Instruction(BaseModel):
    id: str | None = None
    datasource_id: str
    database: str
    table_name: str
    table_schema: str
    table_comment: str | None
    columns: list[ColumnDetail] = []
    table_comment_embedding: Any | None = None
    table_column_embedding: Any | None = None
