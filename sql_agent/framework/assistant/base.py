from abc import abstractmethod
from typing import Any, Generator

from pydantic import BaseModel

from sql_agent.framework.assistant.action import ActionStatus
from sql_agent.framework.assistant.action.base import Action
from sql_agent.protocol import ChatCompletionRequest


class Assistant:
    _actions: list[type[Action]]
    _currentActionIndex: int
    _request: ChatCompletionRequest
    _actions_results: dict[str, dict]

    def __init__(self, request):
        self._actions = self.init_actions()
        self._request = request

    @abstractmethod
    def init_actions(self) -> list[type[Action]]:
        pass

    def run(self) -> Generator:
        size = len(self._actions)
        for i in range(size):
            action = self._actions[i](self._request)
            self.prepare(action)
            self._currentActionIndex = i
            action.execute()
            name = action.get_name()
            result = action.get_result()
            output = {name: result}
            self._actions_results[name] = result
            yield output
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
