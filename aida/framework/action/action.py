from abc import ABC, abstractmethod
from typing import Generic, TypeVar, final

from aida.framework.action import ActionStatus
from aida.framework.action.action_params import ActionParams
from aida.framework.action.action_result import ActionResult

R = TypeVar("R", bound=ActionResult)
P = TypeVar("P", bound=ActionParams)


class Action(Generic[P, R], ABC):
    """
    Agent相关执行动作的父类
    """

    status: ActionStatus = ActionStatus.READY
    params: P
    result: R = None
    name: str = ""

    def __init__(self, params: P):
        self.params = params
        self.name = self.init_name()

    @abstractmethod
    def init_name(self) -> str:
        pass

    @final
    def set_status(self, status: ActionStatus):
        self.status = status

    @final
    @property
    def get_status(self) -> ActionStatus:
        return self.status

    @final
    @property
    def get_result(self) -> R:
        return self.result

    @final
    def set_result(self, result: R):
        self.result = result
