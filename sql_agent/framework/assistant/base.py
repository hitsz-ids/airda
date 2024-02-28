from abc import abstractmethod
from typing import Generator

from sql_agent.framework.assistant.action import ActionStatus
from sql_agent.framework.assistant.action.base import Action


class Assistant:
    _actions: list[type[Action]]
    _currentActionIndex: int
    _question: str

    def __init__(self):
        self._actions = self.init_actions()

    @abstractmethod
    def init_actions(self) -> list[type[Action]]:
        pass

    def run(self, question: str) -> Generator:
        size = len(self._actions)
        for i in range(size):
            action = self._actions[i](question)
            self.prepare(action)
            self._currentActionIndex = i
            action.execute()
            yield action.get_result()
            intercepted = self.complete(action)
            if intercepted:
                break

    def prepare(self, action: Action):
        self.before(action)
        action.set_status(ActionStatus.RUNNING)

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
        action.set_status(ActionStatus.COMPLETE)
        return False
