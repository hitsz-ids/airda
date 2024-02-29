import concurrent.futures
import importlib
import inspect
import os
from abc import ABC
from enum import Enum
from typing import Any, Dict, Type, TypeVar, Union, cast

from dotenv import load_dotenv
from overrides import EnforceOverrides
from pydantic import BaseSettings

setting_class_keys: Dict[str, str] = {
    "sql_agent.server.api.API": "api_impl",
    "sql_agent.db.DB": "db_impl",
    # "sql_agent.model.llm.LLM": "llm_impl",
    # "sql_agent.vector_store.VectorStore": "vector_store_impl",
    "sql_agent.vector_store.doc_index.DocIndex": "doc_index_impl",
    "sql_agent.context_store.ContextStore": "context_store_impl",
}


class LogLevel(Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class EnvSettings:

    load_dotenv()
    api_impl: str = os.getenv("API_IMPL", "sql_agent.server.fastapi")
    db_impl: str = os.getenv("DB", "sql_agent.db.mongo.MongoDB")

    # vector_store_impl: str = os.getenv()(
    #     "VECTOR_STORE", "sql_agent.vector_store.chroma.Chroma"
    # )
    # llm_impl: str = os.getenv()("LLM", "sql_agent.model.llm.vanus.Vanus")
    doc_index_impl: str = os.getenv(
        "DocIndex", "sql_agent.vector_store.doc_index.mongo_doc.MongoDoc"
    )
    context_store_impl: str = os.getenv(
        "CONTEXT_STORE", "sql_agent.context_store.default.DefaultContextStore"
    )
    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    log_level: LogLevel = getattr(LogLevel, log_level_str.upper(), LogLevel.INFO)
    db_name: Union[str, None] = os.getenv("MONGODB_DB_NAME")
    db_uri: Union[str, None] = os.getenv("MONGODB_URI")
    openai_api_key: Union[str, None] = os.getenv("OPENAI_KEY")
    encrypt_key: str = os.getenv("ENCRYPT_KEY")
    application_id: Union[str, None] = os.getenv("APPID")
    model_name: str = os.getenv("model_name")

    embeddings_model_name: Union[str, None] = os.getenv("EMBEDDINGS_MODEL_NAME")
    knowledge_path: Union[str, None] = os.getenv("KNOWLEDGE_PATH")

    def get(self, key: str) -> Any:
        val = self[key]
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, "")


T = TypeVar("T", bound="Component")


class BaseModule(ABC, EnforceOverrides):
    _loaded: bool

    def __init__(self, system: "System"):
        self._loaded = False

    def stop(self) -> None:
        """Idempotently stop this component's execution and free all associated
        resources."""
        self._loaded = False

    def start(self) -> None:
        """Idempotently start this component's execution"""
        self._loaded = True


class System(BaseModule):
    env_settings: EnvSettings
    _instances: Dict[Type[BaseModule], BaseModule]

    def __init__(self, settings: EnvSettings):
        self.settings = settings
        self._instances = {}
        super().__init__(self)

    def get_instance(self, type: Type[T]) -> T:
        """Return an instance of the component type specified. If the system is running,
        the component will be started as well."""

        if inspect.isabstract(type):
            class_full_name = get_class_full_name(type)
            if class_full_name not in setting_class_keys:
                raise ValueError(f"Cannot instantiate abstract type: {type}")
            key = setting_class_keys[class_full_name]
            import_path = self.settings.get(key)
            type = get_class_type(import_path)

        if type not in self._instances:
            impl = type(self)
            self._instances[type] = impl
            if self._loaded:
                impl.start()

        inst = self._instances[type]
        return cast(T, inst)


M = TypeVar("M")


def get_class_type(import_path: str) -> Type[M]:
    """Given a fully qualifed class name, import the module and return the class"""
    module_name, class_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cast(Type[M], cls)


def get_class_full_name(cls: Type[object]) -> str:
    """Given a class, return its fully qualified name"""
    return f"{cls.__module__}.{cls.__name__}"


env_settings = EnvSettings()
works = os.getenv("MAX_WORKERS", "4")
process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=int(works))
