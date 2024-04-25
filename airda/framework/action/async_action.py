from abc import abstractmethod
from typing import TYPE_CHECKING, AsyncGenerator

from airda.framework.action.action import Action, P, R
from airda.framework.action.action_result import ActionResult

if TYPE_CHECKING:
    from airda.framework.agent.context import Context


class AsyncAction(Action[P, R]):
    """
    Action的抽象类，用于异步执行的Action
    """

    @abstractmethod
    def execute(self, context: "Context") -> AsyncGenerator[ActionResult, None]:
        pass
