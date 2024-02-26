from typing import Dict, List, Union

from fastapi import File, UploadFile
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    object: str = "error"
    message: str
    code: int


class ChatCompletionRequest(BaseModel):
    messages: Union[str, List[Dict[str, str]]]
    datasource: str
    database: str
    knowledge: str
    session_id: str


class CompletionKnowledgeLoadRequest(BaseModel):
    file_id: str
    file_name: str
    file: UploadFile = File(...)


class CompletionInstructionSyncRequest(BaseModel):
    instructions: Union[str, List[Dict[str, str]]]
    datasource_id: str
