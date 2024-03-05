from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np

from sql_agent.setting import System
from sql_agent.db import Storage
from sql_agent.llm.embedding_model import EmbeddingModel


system = System()


class SchemaLinking(ABC):
    embedding_model = EmbeddingModel()

    def __init__(self):
        self.storage = system.get_module(Storage)
        self.embedding_model = EmbeddingModel()

    @abstractmethod
    def search(
        self,
        query: str,
        datasource_id: str,
        database: str,
        limit_score: int,
        tok_k: int,
    ) -> Tuple[list[str], list[str]]:
        pass
