from abc import ABC, abstractmethod

from sql_agent.framework.assistant.action.base import Action
from sql_agent.protocol import ChatCompletionRequest


class LlmAction(Action, ABC):
    prompt: str

    def __init__(self, request: ChatCompletionRequest):
        super().__init__(request)
        self.prompt = self.init_prompt(request)

    @abstractmethod
    def init_prompt(self, request: ChatCompletionRequest) -> str:
        pass
