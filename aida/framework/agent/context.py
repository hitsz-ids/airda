from typing import TYPE_CHECKING, TypeVar, cast

from aida.framework import log
from aida.framework.agent import AgentModuleKeys
from aida.framework.module.keys import Keys
from aida.framework.obj.object import Object

if TYPE_CHECKING:
    from aida.framework.agent.module.assistant_manager.assistant.assistant import (
        Assistant,
    )
    from aida.framework.agent.module.assistant_manager.assistant_manager import (
        AssistantManager,
    )
    from aida.framework.agent.module.llm_manager.llm.llm import LLM
    from aida.framework.agent.module.llm_manager.llm_manager import LLMManager
    from aida.framework.agent.module.planner.planner import Planner
T = TypeVar("T")

logger = log.getLogger()

log_loading = "[{}]模块正在加载，cls: [{}]"
log_end = "[{}]模块加载完毕"


class Context(Object):
    modules: dict[Keys, T] = {}

    def load_llm(self, module: type["LLMManager"]):
        logger.debug(log_loading.format("LLMManager", module))
        self._load_by_type(AgentModuleKeys.LLM_MANAGER, module, False, context=self)
        logger.debug(log_end.format("LLMManager"))

    def load_planner(self, module: type["Planner"]):
        logger.debug(log_loading.format("Planner", module))
        self._load_by_type(AgentModuleKeys.PLANNER, module, False, context=self)
        logger.debug(log_end.format("Planner"))

    def load_assistant(self, module: type["AssistantManager"]):
        logger.debug(log_loading.format("AssistantManager", module))
        self._load_by_type(AgentModuleKeys.ASSISTANT_MANAGER, module, False, context=self)
        logger.debug(log_end.format("AssistantManager"))

    def load(self, key: Keys, module: type[T]):
        logger.debug(log_loading.format("Other", module))
        self._load_by_type(key, module, False, context=self)
        logger.debug(log_end.format("Other"))

    def reload(self, key: Keys, module: type[T] | str):
        self._load_by_type(key, module, True)

    def _load_by_type(self, key: Keys, module: type[T], reload: bool, **kwargs):
        if not self.modules.get(key) or reload is True:
            self._create_module(key, module, **kwargs)

    def _create_module(self, key: Keys, cls: type[T], **kwargs):
        module = cls(**kwargs)
        self.modules[key] = module

    def unload(self, key: Keys):
        module = self.modules.get(key)
        if module:
            self.modules.pop(key)

    def get(self, key: Keys, cls: type[T]) -> T:
        module = self.modules.get(key)
        if isinstance(module, cls):
            return cast(T, module)
        return self.modules.get(key)

    def get_llm_manager(self) -> "LLMManager":
        from aida.framework.agent.module.llm_manager.llm_manager import LLMManager

        return self.get(AgentModuleKeys.LLM_MANAGER, LLMManager)

    def get_llm(self, key: Keys) -> "LLM":
        return self.get_llm_manager().get_llm(key)

    def get_assistant_manger(self) -> "AssistantManager":
        from aida.framework.agent.module.assistant_manager.assistant_manager import (
            AssistantManager,
        )

        return self.get(AgentModuleKeys.ASSISTANT_MANAGER, AssistantManager)

    def get_assistant(self, key: Keys) -> type["Assistant"]:
        return self.get_assistant_manger().get_assistant(key)

    def get_planner(self) -> "Planner":
        from aida.framework.agent.module.planner.planner import Planner

        return self.get(AgentModuleKeys.PLANNER, Planner)
