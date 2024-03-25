from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, validator


class Datasource(BaseModel):
    id: str | None = None
    type: str | None = None
    host: str
    port: int
    database: str
    user_name: str
    password: str
    config: dict | None = None


class Knowledge(BaseModel):
    id: str | None = None
    source: str
    content: str
    content_embedding: Any


class EmbeddingInstruction(BaseModel):
    id: str | None = None
    datasource_id: str
    database: str
    table_name: str
    table_comment: str
    table_comment_embedding: Any
    column_embedding: Any


class DBEmbeddingStatus(Enum):
    EMBEDDING = 1
    SUCCESS = 2
    FAILED = 3
    STOP = 4


class InstructionEmbeddingRecord(BaseModel):
    id: str | None = None
    datasource_id: str
    status: int = DBEmbeddingStatus.EMBEDDING.value


class KnowledgeEmbeddingStatus(Enum):
    EMBEDDING = 1
    SUCCESS = 2
    FAILED = 3
    STOP = 4


class KnowledgeEmbeddingRecord(BaseModel):
    id: str | None = None
    file_path: str
    file_id: str
    status: int = KnowledgeEmbeddingStatus.EMBEDDING.value


class ForeignKeyDetail(BaseModel):
    field_name: str
    reference_table: str


class ColumnDetail(BaseModel):
    name: str
    is_primary_key: bool = False
    data_type: str = "str"
    description: str | None
    low_cardinality: bool = False
    categories: list[Any] | None
    foreign_key: ForeignKeyDetail | None


class TableDescriptionStatus(Enum):
    NOT_SYNCHRONIZED = "NOT_SYNCHRONIZED"
    SYNCHRONIZING = "SYNCHRONIZING"
    DEPRECATED = "DEPRECATED"
    SYNCHRONIZED = "SYNCHRONIZED"
    FAILED = "FAILED"


class TableDescription(BaseModel):
    id: str | None
    datasource_id: str
    name: str
    description: str | None
    table_schema: str | None
    columns: list[ColumnDetail] = []
    examples: list = []
    last_schema_sync: datetime | None
    status: str = TableDescriptionStatus.SYNCHRONIZED.value
    error_message: str | None

    @validator("last_schema_sync", pre=True)
    def parse_datetime_with_timezone(cls, value):
        if not value:
            return None
        return value.replace(tzinfo=timezone.utc)  # Set the timezone to UTC


class Instruction(BaseModel):
    id: str | None = None
    instruction: TableDescription
    datasource_id: str
    database: str
    table_name: str
