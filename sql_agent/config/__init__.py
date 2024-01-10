import importlib
import inspect
import os
from abc import ABC
from typing import Any, Dict, Type, TypeVar, cast, Union

from dotenv import load_dotenv
from overrides import EnforceOverrides
from pydantic import BaseSettings

_abstract_type_keys: Dict[str, str] = {
    "sql_agent.api.API": "api_impl",
    "sql_agent.db.DB": "db_impl",
    "sql_agent.llm.LLM": "llm_impl",
    "sql_agent.vector_store.VectorStore": "vector_store_impl",
    "sql_agent.vector_store.doc_index.DocIndex": "doc_index_impl",
    "sql_agent.context_store.ContextStore": "context_store_impl"
}


class Settings(BaseSettings):
    load_dotenv()
    api_impl: str = os.environ.get("API_SERVER", "sql_agent.api.fastapi.FastAPI")
    db_impl: str = os.environ.get("DB", "sql_agent.db.mongo.MongoDB")

    vector_store_impl: str = os.environ.get(
        "VECTOR_STORE", "sql_agent.vector_store.chroma.Chroma"
    )
    llm_impl: str = os.environ.get(
        "LLM", "sql_agent.llm.vanus.Vanus"
    )
    doc_index_impl: str = os.environ.get(
        "DocIndex", "sql_agent.vector_store.doc_index.chroma_doc.ChromaDoc"
    )
    context_store_impl:str=os.environ.get(
        "CONTEXT_STORE", "sql_agent.context_store.default.DefaultContextStore"
    )

    db_name: Union[str, None] = os.environ.get("MONGODB_DB_NAME")
    db_uri: Union[str, None] = os.environ.get("MONGODB_URI")
    redis_uri = os.environ.get('REDIS_URI')
    redis_port = os.environ.get('REDIS_PORT')
    redis_pwd = os.environ.get('REDIS_PWD')
    openai_api_key: Union[str, None] = os.environ.get("OPENAI_KEY")
    encrypt_key: str = os.environ.get("ENCRYPT_KEY")
    s3_aws_access_key_id: Union[str, None] = os.environ.get("S3_AWS_ACCESS_KEY_ID")
    s3_aws_secret_access_key: Union[str, None] = os.environ.get("S3_AWS_SECRET_ACCESS_KEY")
    application_id: Union[str, None] = os.environ.get("APPID")
    model_name: str = os.environ.get("model_name")
    business_server_url: Union[str, None] = os.environ.get('BUSINESS_SERVER')
    persist_directory: Union[str, None] = os.environ.get('PERSIST_DIRECTORY')
    embeddings_model_name: Union[str, None] = os.environ.get('EMBEDDINGS_MODEL_NAME')

    def require(self, key: str) -> Any:
        val = self[key]
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


T = TypeVar("T", bound="Component")


class Component(ABC, EnforceOverrides):
    _running: bool

    def __init__(self, system: "System"):  # noqa: ARG002
        self._running = False

    def stop(self) -> None:
        """Idempotently stop this component's execution and free all associated
        resources."""
        self._running = False

    def start(self) -> None:
        """Idempotently start this component's execution"""
        self._running = True


class System(Component):
    settings: Settings
    _instances: Dict[Type[Component], Component]

    def __init__(self, settings: Settings):
        self.settings = settings
        self._instances = {}
        super().__init__(self)

    def instance(self, type: Type[T]) -> T:
        """Return an instance of the component type specified. If the system is running,
        the component will be started as well."""

        if inspect.isabstract(type):
            type_fqn = get_fqn(type)
            if type_fqn not in _abstract_type_keys:
                raise ValueError(f"Cannot instantiate abstract type: {type}")
            key = _abstract_type_keys[type_fqn]
            fqn = self.settings.require(key)
            type = get_class(fqn, type)

        if type not in self._instances:
            impl = type(self)
            self._instances[type] = impl
            if self._running:
                impl.start()

        inst = self._instances[type]
        return cast(T, inst)


C = TypeVar("C")


def get_class(fqn: str, type: Type[C]) -> Type[C]:  # noqa: ARG001
    """Given a fully qualifed class name, import the module and return the class"""
    module_name, class_name = fqn.rsplit(".", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cast(Type[C], cls)


def get_fqn(cls: Type[object]) -> str:
    """Given a class, return its fully qualified name"""
    return f"{cls.__module__}.{cls.__name__}"
