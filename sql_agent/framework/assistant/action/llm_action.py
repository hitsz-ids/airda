from abc import ABC, abstractmethod

from framework.assistant.action.base import Action


class LlmAction(Action, ABC):
    prompt: str
    pass

    @abstractmethod
    def initPrompt(self, _question) -> str:
        pass
