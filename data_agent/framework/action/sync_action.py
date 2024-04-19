from abc import abstractmethod
from typing import TYPE_CHECKING

from data_agent.framework.action.action import Action, P, R

if TYPE_CHECKING:
    from data_agent.framework.agent.context import Context


class SyncAction(Action[P, R]):
    """
    Action的抽象类，用于同步执行的Action
    """

    @abstractmethod
    def execute(self, context: "Context") -> R:
        pass
