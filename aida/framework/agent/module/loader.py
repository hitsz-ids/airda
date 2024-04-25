import importlib
from typing import TYPE_CHECKING, TypeVar, cast

from aida.framework.exception.module_type_error import ModuleTypeError
from aida.framework.module.dynamic import DynamicModule
from aida.framework.module.immediate import Immediate
from aida.framework.module.keys import Keys
from aida.framework.module.lazy import Lazy
from aida.framework.obj.object import Object

if TYPE_CHECKING:
    from aida.framework.agent.context import Context

M = TypeVar("M", bound=DynamicModule)


class Loader(Object):
    context: "Context"
    immediate: dict[Keys, M] = {}
    lazy: dict[Keys, type[M]] = {}

    def __init__(self, context: "Context"):
        self.context = context

    def load(self, key: Keys, module: type[M] | str, **kwargs):
        if isinstance(module, str):
            self._load_by_path(key, module, False, **kwargs)
        else:
            self._load_by_type(key, module, False, **kwargs)

    def reload(self, key: Keys, module: type[M] | str, **kwargs):
        if isinstance(module, str):
            self._load_by_path(key, module, True, **kwargs)
        else:
            self._load_by_type(key, module, True, **kwargs)

    def _load_by_type(self, key: Keys, module: type[M], reload: bool, **kwargs):
        if issubclass(module, Immediate):
            if not self.immediate.get(key) or reload is True:
                self._create_module(key, module, **kwargs)
        elif issubclass(module, Lazy):
            if not self.lazy.get(key) or reload is True:
                self._create_module(key, module)

    def _load_by_path(self, key: Keys, module: str, reload: bool, **kwargs):
        module_name, class_name = module.rsplit(".", 1)
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        if issubclass(cls, Immediate):
            if not self.immediate[key] or reload is True:
                self._create_module(key, cls, **kwargs)
        elif issubclass(cls, Lazy):
            if not self.lazy[key] or reload is True:
                self._create_module(key, cls)

    def _create_module(self, key: Keys, cls: type[M], **kwargs):
        if issubclass(cls, Immediate):
            module = cls(**kwargs)
            self.immediate[key] = module
        elif issubclass(cls, Lazy):
            self.lazy[key] = cls
        else:
            raise ModuleTypeError("加载的模块必须为Immediate或Lazy")

    def unload(self, key: Keys):
        module = self.immediate.get(key)
        if module:
            self.immediate.pop(key)
        else:
            self.lazy.pop(key)

    def get_immediate(self, key: Keys, module_type: type[M]) -> M | None:
        module = self.immediate.get(key)
        if module is None:
            return None
        if issubclass(type(module), module_type):
            return cast(M, self.immediate[key])
        else:
            raise ModuleTypeError("获取的Immediate模块类型不匹配")

    def get_lazy(self, key: Keys, module_type: type[M]) -> type[M] | None:
        module = self.lazy.get(key)
        if module is None:
            return None
        if issubclass(module, module_type):
            return module
        else:
            raise ModuleTypeError("获取的Lazy模块类型不匹配")
