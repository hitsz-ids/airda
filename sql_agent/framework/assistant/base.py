from abc import abstractmethod
from typing import Type

from framework.assistant.action import ActionStatus
from framework.assistant.action.base import Action


class Assistant:
    _actions: list[Type[Action]]
    _current: int
    _question: str
    def __init__(self):
        self._actions = self.initActions()

    @abstractmethod
    def initActions(self) -> list[Type[Action]]:
        pass

    def run(self, question: str):
        size = len(self._actions)
        for i in range(size):
            i = yield i
            action = self._actions[i]()
            self._current = action
            self.prepare(action)
            action.execute()
            intercepted = self.complete(action)
            if intercepted:
                break

    def prepare(self, action: Action):
        self.before(action)
        action.setStatus(ActionStatus.RUNNING)
        pass

    @abstractmethod
    def before(self, action: Action):
        pass

    @abstractmethod
    def after(self, action: Action):
        pass

    def complete(self, action: Action) -> bool:
        try:
            self.after(action)
        except Exception:
            pass
        action.setStatus(ActionStatus.COMPLETE)
        return False
