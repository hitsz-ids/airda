import time
from typing import Optional, Literal

import shortuuid
from fastapi import File, UploadFile
from pydantic import BaseModel, Field

from sql_agent.db.repositories.types import Instruction


class ErrorResponse(BaseModel):
    object: str = "error"
    message: str
    code: int


class ChatCompletionRequest(BaseModel):
    messages: list[dict[str, str]]
    datasource_id: str
    database: str
    knowledge: str
    session_id: str
    file_path: str


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


class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


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
