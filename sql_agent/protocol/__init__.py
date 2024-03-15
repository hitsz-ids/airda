import time
from typing import Literal, Optional

import shortuuid
from fastapi import File, UploadFile
from pydantic import BaseModel, Field

from sql_agent.db.repositories.types import Instruction


class ErrorResponse(BaseModel):
    object: str = "error"
    message: str
    code: int


class ChatCompletionRequest(BaseModel):
    question: str
    datasource_id: str
    database: str
    knowledge: str
    session_id: str
    sql_type: str = "mysql"
    file_name: str
    file_id: str


class CompletionKnowledgeLoadRequest(BaseModel):
    file_id: str
    file_name: str
    file: UploadFile = File(...)


class CompletionKnowledgeStatusRequest(BaseModel):
    id: str


class CompletionKnowledgeStopRequest(BaseModel):
    id: str


class DatasourceAddRequest(BaseModel):
    type: str
    host: str
    port: int
    database: str
    user_name: str
    password: str
    config: dict[str, str] | None = None


class DatasourceUpdateRequest(BaseModel):
    id: str
    host: str
    port: int
    database: str
    user_name: str
    password: str
    config: dict[str, str] | None = None


class DatasourceDeleteRequest(BaseModel):
    id: str


class CompletionInstructionSyncRequest(BaseModel):
    instructions: list[Instruction]
    datasource_id: str


class CompletionInstructionSyncStatusRequest(BaseModel):
    id: str


class CompletionInstructionSyncStopRequest(BaseModel):
    id: str


ChatMessage = dict[Literal["role", "content"], str]


class DeltaMessage(BaseModel):
    role: str
    content: str


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length"]] = None


class ChatCompletionStreamResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{shortuuid.random()}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: list[ChatCompletionResponseStreamChoice]


class Question(BaseModel):
    id: str | None = None
    question: str
    datasource_id: str
    database: str
