import concurrent.futures
import importlib
import inspect
import os
from abc import ABC
from enum import Enum
from typing import Any, Type, TypeVar, cast

from dotenv import load_dotenv

from sql_agent.framework.types import Singleton


class LogLevel(Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


T = TypeVar("T", bound="Component")
M = TypeVar("M")


class BaseModule(ABC):
    _loaded: bool

    def __init__(self):
        self._loaded = False

    def stop(self) -> None:
        """Idempotently stop this component's execution and free all associated
        resources."""
        self._loaded = False

    def start(self) -> None:
        """Idempotently start this component's execution"""
        self._loaded = True


setting_module_keys: dict[str, str] = {
    "sql_agent.server.api.API": "api_impl",
    "sql_agent.db.Storage": "storage_impl",
    "sql_agent.llm.LLM": "llm_impl",
}


class EnvSettings(metaclass=Singleton):
    load_dotenv()

    # 接口实现类路径
    api_impl: str = os.getenv("API_IMPL", "sql_agent.server.api.api.APIImpl")

    # 存储实现类路径
    storage_impl: str = os.getenv("Storage", "sql_agent.db.mongo.MongoStorage")

    # 语言大模型实现类路径
    llm_impl: str = os.getenv("LLM", "sql_agent.llm.openai.OpenAILLM")

    # 向量化模型名称
    embeddings_model_name: str = os.getenv("EMBEDDINGS_MODEL_NAME", "infgrad/stella-large-zh-v2")

    # mongo环境变量
    mongodb_uri: str | None = os.getenv("MONGODB_URI")
    mongodb_db_name: str | None = os.getenv("MONGODB_DB_NAME")
    mongodb_username: str | None = os.getenv("MONGODB_USERNAME")
    mongodb_password: str | None = os.getenv("MONGODB_PASSWORD")

    # openai配置
    openai_api_key: str | None = os.getenv("OPENAI_KEY")
    model_name: str = os.getenv("model_name")

    # 知识库缓存路径
    knowledge_path: str | None = os.getenv("KNOWLEDGE_PATH")

    # vanus 代理 appid
    application_id: str | None = os.getenv("APPID")

    # 最大embedding最大并发数
    max_works = os.getenv("MAX_WORKERS", "4")

    log_level: str = os.getenv("LOG_LEVEL", LogLevel.INFO.value)

    def get(self, key: str) -> Any:
        val = self[key]
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, "")


env_settings = EnvSettings()


class System(metaclass=Singleton):
    _cache_modules = {}
    env_settings: EnvSettings

    def __init__(self):
        super().__init__()
        self.env_settings = env_settings

    def get_module(self, module_type: Type[T]) -> T:
        """Return an instance of the component type specified. If the system is running,
        the component will be started as well."""

        if inspect.isabstract(module_type):
            module_full_name = get_module_full_name(module_type)
            if module_full_name not in setting_module_keys:
                raise ValueError(f"module: {module_type}, not in setting_module_keys")
            key = setting_module_keys[module_full_name]
            import_path = self.env_settings.get(key)
            module_type = get_class_type(import_path)

        if module_type not in self._cache_modules:
            module_inst = module_type()
            self._cache_modules[module_type] = module_inst

        return cast(T, self._cache_modules[module_type])

    def get_process_pool(self):
        return concurrent.futures.ProcessPoolExecutor(max_workers=int(env_settings.max_works))


def get_class_type(import_path: str) -> Type[M]:
    """Given a fully qualifed class name, import the module and return the class"""
    module_name, class_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cast(Type[M], cls)


def get_module_full_name(cls: Type[object]) -> str:
    """Given a class, return its fully qualified name"""
    return f"{cls.__module__}.{cls.__name__}"
