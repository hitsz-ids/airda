from abc import ABC, abstractmethod

from sql_agent.framework.assistant.action.base import Action


class LlmAction(Action, ABC):
    prompt: str

    @abstractmethod
    def init_prompt(self, _question) -> str:
        pass
