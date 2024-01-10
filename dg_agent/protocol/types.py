from pydantic import BaseModel
from typing import Union


class GoldenRecord(BaseModel):
    id: Union[str, None] = None
    question: str
    sql_query: str
    db_connection_id: str


class Question(BaseModel):
    id: Union[str, None] = None
    question: str
    db_connection_id: str


class Instruction(BaseModel):
    id: Union[str, None] = None
    instruction: str
    db_connection_id: str
