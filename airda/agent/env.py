import os
from enum import Enum

from airda.framework.setting.env_manager import Env
from airda.framework.utils import singleton


class LogLevel(Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


@singleton
class DataAgentEnv(Env):
    # 向量化模型名称
    EMBEDDINGS_MODEL_NAME: str | None

    # mongo环境变量
    MONGODB_URI: str | None
    MONGODB_DB_NAME: str | None
    MONGODB_USERNAME: str | None
    MONGODB_PASSWORD: str | None

    # openai配置
    OPENAI_API_KEY: str | None
    MODEL_NAME: str

    # 最大embedding最大并发数
    MAX_WORKS: str | None

    def init(self):
        self.EMBEDDINGS_MODEL_NAME = os.getenv(
            "EMBEDDINGS_MODEL_NAME", "infgrad/stella-large-zh-v2"
        )

        # mongo环境变量
        self.MONGODB_URI = os.getenv("MONGODB_URI")
        self.MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
        self.MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
        self.MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")

        # openai配置
        self.OPENAI_API_KEY = os.getenv("OPENAI_KEY")
        self.MODEL_NAME = os.getenv("MODEL_NAME")

        # 最大embedding最大并发数
        self.MAX_WORKS = os.getenv("MAX_WORKERS", "4")
