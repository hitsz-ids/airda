import os
from enum import Enum

from aida.framework.setting.env_manager import Env
from aida.framework.utils import singleton


class LogLevel(Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


@singleton
class DataAgentEnv(Env):
    # 向量化模型名称
    embeddings_model_name: str | None

    # mongo环境变量
    mongodb_uri: str | None
    mongodb_db_name: str | None
    mongodb_username: str | None
    mongodb_password: str | None

    # openai配置
    openai_api_key: str | None
    model_name: str

    # 知识库缓存路径
    knowledge_path: str | None

    # vanus 代理 appid
    application_id: str | None

    # 最大embedding最大并发数
    max_works: str | None

    log_level: str | None

    def init(self):
        self.embeddings_model_name = os.getenv(
            "EMBEDDINGS_MODEL_NAME", "infgrad/stella-large-zh-v2"
        )

        # mongo环境变量
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.mongodb_db_name = os.getenv("MONGODB_DB_NAME")
        self.mongodb_username = os.getenv("MONGODB_USERNAME")
        self.mongodb_password = os.getenv("MONGODB_PASSWORD")

        # openai配置
        self.openai_api_key = os.getenv("OPENAI_KEY")
        self.model_name = os.getenv("model_name")

        # 知识库缓存路径
        self.knowledge_path = os.getenv("KNOWLEDGE_PATH")

        # vanus 代理 appid
        self.application_id = os.getenv("APPID")

        # 最大embedding最大并发数
        self.max_works = os.getenv("MAX_WORKERS", "4")

        self.log_level = os.getenv("LOG_LEVEL", LogLevel.INFO.value)
