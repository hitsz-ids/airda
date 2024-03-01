from enum import Enum
from typing import Any, Union

from pydantic import BaseModel


class Datasource(BaseModel):
    id: Union[str, None] = None
    type: Union[str, None] = None
    host: str
    port: int
    database: str
    user_name: str
    password: str
    config: Union[dict, None] = None


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


class InstructionEmbeddingRecord(BaseModel):
    id: Union[str, None] = None
    datasource_id: str
    status: int = DBEmbeddingStatus.EMBEDDING.value


class KnowledgeEmbeddingStatus(Enum):
    EMBEDDING = 1
    SUCCESS = 2
    FAILED = 3
    STOP = 4


class KnowledgeEmbeddingRecord(BaseModel):
    id: Union[str, None] = None
    file_path: str
    file_id: str
    status: int = KnowledgeEmbeddingStatus.EMBEDDING.value
