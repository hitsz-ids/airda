from abc import ABC, abstractmethod
from typing import AsyncGenerator

from sql_agent.framework.assistant.action import (
    ActionResult,
    ActionResultScope,
    ActionStatus,
)
from sql_agent.protocol import ChatCompletionRequest


class BaseAction(ABC):
    _name: str = ""
    _request: ChatCompletionRequest
    _status: ActionStatus = ActionStatus.READY
    _result: ActionResult
    _actions_results: dict[str, dict]

    def __init__(
        self, request: ChatCompletionRequest, action_results: dict[str, dict]
    ) -> None:
        super().__init__()
        self._request = request
        self._actions_results = action_results
        self._name = self.init_name()
        self._result = {}

    @abstractmethod
    def init_name(self) -> str:
        pass

    def set_result(
        self, result: dict, scope: ActionResultScope = ActionResultScope.user
    ):
        self._result = ActionResult(scope=scope, result=result)

    def get_result(self):
        return self._result

    def get_name(self) -> str:
        return self._name

    def set_status(self, status: ActionStatus):
        self._status = status

    def get_status(self) -> ActionStatus:
        return self._status


class Action(BaseAction, ABC):
    @abstractmethod
    def execute(self):
        pass


class AsyncAction(BaseAction, ABC):
    @abstractmethod
    async def execute(self) -> AsyncGenerator[str, None]:
        pass
