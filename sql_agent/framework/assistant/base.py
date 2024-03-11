from abc import abstractmethod
from typing import AsyncGenerator

from sql_agent.framework.assistant.action import ActionResultScope, ActionStatus
from sql_agent.framework.assistant.action.base import Action, AsyncAction
from sql_agent.protocol import ChatCompletionRequest
from sql_agent.setting import System

system = System()


class Assistant:
    _actions: list[type[Action]]
    _currentActionIndex: int
    _request: ChatCompletionRequest
    _actions_results: dict[str, dict]

    def __init__(self, request):
        self._actions = self.init_actions()
        self._request = request
        self._actions_results = {}

    @abstractmethod
    def init_actions(self) -> list[type[Action]]:
        pass

    async def run(self) -> AsyncGenerator[str, None]:
        size = len(self._actions)
        for i in range(size):
            action = self._actions[i](self._request, self._actions_results)
            self.prepare(action)
            self._currentActionIndex = i
            if isinstance(action, AsyncAction):
                async for item in action.execute():
                    if item:
                        yield item
            else:
                action.execute()
                if action.get_result().scope == ActionResultScope.user:
                    yield action.get_result().result

            name = action.get_name()
            result = action.get_result()
            self._actions_results[name] = result.result
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
