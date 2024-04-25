from abc import ABC

from airda.agent.action.searcher import Searcher
from airda.framework.action.action import Action
from airda.framework.agent.module.assistant_manager.assistant.assistant import (
    Assistant,
)


class ChatAssistant(Assistant, ABC):
    def before(self, action: Action):
        pass

    def after(self, action: Action):
        pass

    def init_actions(self) -> list[type[Action]]:
        return [Searcher]

    def complete(self, action: Action) -> bool:
        return False
