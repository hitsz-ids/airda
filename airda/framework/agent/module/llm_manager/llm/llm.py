from abc import abstractmethod
from typing import AsyncGenerator, Literal

from airda.framework.module.lazy import Lazy

ChatMessage = dict[Literal["role", "content"], str]


class LLM(Lazy):
    def __init__(self, **kwargs):
        super().__init__()

    @abstractmethod
    def chat_completion(self, messages: list[ChatMessage], model_name: str, session_id: str) -> str:
        pass

    @abstractmethod
    def chat_completion_stream(
        self, messages: list[ChatMessage], model_name: str, session_id: str
    ) -> AsyncGenerator[str, None]:
        pass
