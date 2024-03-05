from fastapi import File, UploadFile
from pydantic import BaseModel

from sql_agent.db.repositories.types import Instruction


class ErrorResponse(BaseModel):
    object: str = "error"
    message: str
    code: int


class ChatCompletionRequest(BaseModel):
    messages: str | list[dict[str, str]]
    datasource: str
    database: str
    knowledge: str
    session_id: str


class CompletionKnowledgeLoadRequest(BaseModel):
    file_id: str
    file_name: str
    file: UploadFile = File(...)


class DatasourceAddRequest(BaseModel):
    type: str
    host: str
    port: int
    database: str
    user_name: str
    password: str
    config: dict[str, str] | None = None


class CompletionInstructionSyncRequest(BaseModel):
    instructions: str | list[Instruction]
    datasource_id: str


class CompletionInstructionSyncStatusRequest(BaseModel):
    id: str


class CompletionInstructionSyncStopRequest(BaseModel):
    id: str
