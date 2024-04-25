from abc import abstractmethod
from typing import TYPE_CHECKING

from airda.framework.action.action import Action, P, R

if TYPE_CHECKING:
    from airda.framework.agent.context import Context


class SyncAction(Action[P, R]):
    """
    Action的抽象类，用于同步执行的Action
    """

    @abstractmethod
    def execute(self, context: "Context") -> R:
        pass
