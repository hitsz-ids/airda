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
    "sql_agent.rag.knowledge.service.KnowledgeService": "knowledge_service",
    # "sql_agent.model.llm.LLM": "llm_impl",
    # "sql_agent.vector_store.VectorStore": "vector_store_impl",
    # "sql_agent.context_store.ContextStore": "context_store_impl",
}


class EnvSettings(metaclass=Singleton):
    load_dotenv()

    api_impl: str = os.getenv("API_IMPL", "sql_agent.server.fastapi")
    storage_impl: str = os.getenv("DB", "sql_agent.db.mongo.MongoStorage")

    knowledge_service: str = os.getenv(
        "KNOWLEDGE_SERVICE", "sql_agent.rag.knowledge.service.KnowledgeService"
    )

    # vector_store_impl: str = os.getenv(
    #     "VECTOR_STORE", "sql_agent.vector_store.chroma.Chroma"
    # )
    # context_store_impl: str = os.getenv(
    #     "CONTEXT_STORE", "sql_agent.context_store.default.DefaultContextStore"
    # )
    # llm_impl: str = os.getenv("LLM", "sql_agent.model.llm.vanus.Vanus")

    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    try:
        log_level: str = LogLevel[log_level_str.upper()].value
    except KeyError:
        log_level: str = LogLevel.INFO.value

    db_name: str | None = os.getenv("MONGODB_DB_NAME")
    db_uri: str | None = os.getenv("MONGODB_URI")
    openai_api_key: str | None = os.getenv("OPENAI_KEY")
    encrypt_key: str = os.getenv("ENCRYPT_KEY")
    application_id: str | None = os.getenv("APPID")
    model_name: str = os.getenv("model_name")

    embeddings_model_name: str | None = os.getenv("EMBEDDINGS_MODEL_NAME")
    knowledge_path: str | None = os.getenv("KNOWLEDGE_PATH")

    def get(self, key: str) -> Any:
        val = self[key]
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, "")


def get_class_type(import_path: str) -> Type[M]:
    """Given a fully qualifed class name, import the module and return the class"""
    module_name, class_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cast(Type[M], cls)


def get_module_full_name(cls: Type[object]) -> str:
    """Given a class, return its fully qualified name"""
    return f"{cls.__module__}.{cls.__name__}"


env_settings = EnvSettings()


class System(metaclass=Singleton):
    _cache_modules = {}

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
            module_inst.start()

        return cast(T, self._cache_modules[module_type])


works = os.getenv("MAX_WORKERS", "4")
process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=int(works))
