from abc import abstractmethod
from typing import AsyncGenerator

from sql_agent.protocol import ChatMessage
from sql_agent.setting import BaseModule, System


class LLM(BaseModule):
    def __init__(self):
        super().__init__()
        self.system = System()

    @abstractmethod
    def chat_completion(
        self, messages: list[ChatMessage], model_name: str, session_id: str
    ) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    async def chat_completion_stream(
        self, messages: list[ChatMessage], model_name: str, session_id: str
    ) -> AsyncGenerator[str, None]:
        pass
