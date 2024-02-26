from enum import Enum
from typing import Any, Union

from pydantic import BaseModel


class Knowledge(BaseModel):
    id: Union[str, None] = None
    source: str
    content: str
    content_embedding: Any


class Instruction(BaseModel):
    id: Union[str, None] = None
    instruction: dict
    datasource_id: str
    database: str
    table_name: str


class EmbeddingInstruction(BaseModel):
    id: Union[str, None] = None
    db_connection_id: str
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


class InstructionSyncRecord(BaseModel):
    id: Union[str, None] = None
    datasource_id: str
    status: int = DBEmbeddingStatus.EMBEDDING.value
