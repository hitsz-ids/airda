from abc import ABC, abstractmethod

from sql_agent.framework.assistant.action.base import AsyncAction
from sql_agent.protocol import ChatMessage


class LlmAction(AsyncAction, ABC):
    prompt: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = self.init_prompt()

    @abstractmethod
    def init_prompt(self) -> str:
        pass

    def make_message(self, role: str = "user") -> ChatMessage:
        return {"role": role, "content": self.prompt}
