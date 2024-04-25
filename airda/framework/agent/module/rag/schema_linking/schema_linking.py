from abc import abstractmethod

from airda.framework import log
from airda.framework.agent.module.rag.embedding.embedding_model import (
    EmbeddingModel,
)
from airda.framework.module.immediate import Immediate

logger = log.getLogger()


class SchemaLinking(Immediate):
    embedding_model: EmbeddingModel

    #
    def __init__(self, model: EmbeddingModel, **kwargs):
        super().__init__(**kwargs)
        self.embedding_model = model

    @abstractmethod
    def search(
        self,
        question_embedding: str,
        batch_tables: list[str],
        table_embedding,
        columns_embedding,
        limit_score: int = 65,
        tok_k: int = 100,
    ) -> tuple[list[str], list[str]]:
        pass
