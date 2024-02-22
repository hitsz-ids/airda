from typing import Type

from assistants.action.searcher import Searcher
from framework.assistant.action.base import Action
from framework.assistant.base import Assistant


class ChatAssistant(Assistant):
    _prompt: "我是一个什么xxx"
    def before(self, action: Action):
        pass

    def after(self, action: Action):
        pass

    def initActions(self) -> list[Type[Action]]:
        return [Searcher]

    def prepare(self, action: Action):
        pass

    def complete(self, action: Action) -> bool:
        return False
