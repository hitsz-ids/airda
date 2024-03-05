from abc import abstractmethod, ABC
from typing import Any

from sql_agent.framework.assistant.action import ActionStatus
from sql_agent.protocol import ChatCompletionRequest


class Action(ABC):
    _result: str = ""
    _request: ChatCompletionRequest
    _name: str = ""
    _status: ActionStatus = ActionStatus.READY

    def __init__(self, *args, **kwargs):
        self._request = args[0]
        self._name = self.init_name()

    @abstractmethod
    def init_name(self) -> str:
        pass

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        return False

    def get_result(self):
        return self._result

    def get_name(self) -> str:
        return self._name

    def set_status(self, status: ActionStatus):
        self._status = status
