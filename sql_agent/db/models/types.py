from pydantic import BaseModel, validator
from typing import Union, Any
from datetime import datetime, timezone
from enum import Enum


class GoldenRecord(BaseModel):
    id: Union[str, None] = None
    question: str
    sql_query: str
    db_connection_id: str


class TableDescriptionStatus(Enum):
    NOT_SYNCHRONIZED = "NOT_SYNCHRONIZED"
    SYNCHRONIZING = "SYNCHRONIZING"
    DEPRECATED = "DEPRECATED"
    SYNCHRONIZED = "SYNCHRONIZED"
    FAILED = "FAILED"


class ForeignKeyDetail(BaseModel):
    field_name: str
    reference_table: str


class ColumnDetail(BaseModel):
    name: str
    is_primary_key: bool = False
    data_type: str = "str"
    description: Union[str, None]
    low_cardinality: bool = False
    categories: Union[list[Any], None]
    foreign_key: Union[ForeignKeyDetail, None]


class TableDescription(BaseModel):
    id: Union[str, None]
    db_connection_id: str
    table_name: str
    description: Union[str, None]
    table_schema: Union[str, None]
    columns: list[ColumnDetail] = []
    examples: list = []
    last_schema_sync: Union[datetime, None]
    status: str = TableDescriptionStatus.SYNCHRONIZED.value
    error_message: Union[str, None]

    @validator("last_schema_sync", pre=True)
    def parse_datetime_with_timezone(cls, value):
        if not value:
            return None
        return value.replace(tzinfo=timezone.utc)  # Set the timezone to UTC


class NlQuestion(BaseModel):
    question: str
    answer: str
    db_connection_id: str
