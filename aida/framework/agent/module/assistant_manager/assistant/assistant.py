import logging
import traceback
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generic, Optional, TypeVar, final

if TYPE_CHECKING:
    from aida.framework.agent.context import Context

from aida.framework.action import ActionStatus
from aida.framework.action.action import Action
from aida.framework.agent.module.assistant_manager.assistant.assistant_params import (
    AssistantParams,
)
from aida.framework.agent.module.assistant_manager.assistant.assistant_result import (
    AssistantResult,
)
from aida.framework.module.lazy import Lazy

AP = TypeVar("AP", bound=AssistantParams)

logger = logging.getLogger(__name__)


class Assistant(Lazy, Generic[AP], ABC):
    actions: list[type[Action]]
    previous: dict[type[Action], Action] = {}
    currentActionIndex: int
    params: AP
    context: Optional["Context"]

    def __init__(self, params: AP, context: "Context"):
        super().__init__()
        self.actions = self.init_actions()
        self.params = params
        self.context = context

    @final
    @property
    def get_params(self) -> AP:
        return self.params

    def prepare(self, cls: type[Action]) -> Action:
        return self.before(cls)

    async def run(self) -> AsyncGenerator[Any, None]:
        try:
            size = len(self.actions)
            for i in range(size):
                cls = self.actions[i]
                m_action = self.prepare(cls)
                self.currentActionIndex = i
                async for item in self.start(m_action):
                    if item.output is not None:
                        yield item.output
                    m_action.set_result(item.result)
                self.complete(m_action)
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            raise e

    def complete(self, m_action: Action) -> bool:
        cls = self.after(m_action)
        m_action.set_status(ActionStatus.COMPLETE)
        self.previous[cls] = m_action
        return False

    def get_previous(self) -> dict[type[Action], Action]:
        return self.previous

    @abstractmethod
    async def start(self, m_action: Action) -> AsyncGenerator[AssistantResult, None]:
        pass

    @abstractmethod
    def before(self, cls: type[Action]) -> Action:
        pass

    @abstractmethod
    def after(self, m_action: Action) -> type[Action]:
        pass

    @abstractmethod
    def init_actions(self) -> list[type[Action]]:
        pass
