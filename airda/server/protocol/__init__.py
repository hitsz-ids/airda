from datetime import datetime
from typing import Literal, Optional

import shortuuid
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    object: str = "error"
    message: str
    code: int


class ChatCompletionRequest(BaseModel):
    question: str
    datasource_name: str


class AddDatasourceRequest(BaseModel):
    name: str
    host: str
    port: int
    database: str
    kind: str
    username: str | None
    password: str | None


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
    created: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    model: str
    choices: list[ChatCompletionResponseStreamChoice]


class Question(BaseModel):
    id: str | None = None
    question: str
    datasource_id: str
    database: str
