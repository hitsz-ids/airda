import numpy as np

from airda.agent import log
from airda.framework.agent.module.rag.embedding.embedding_model import EmbeddingModel
from airda.framework.agent.module.rag.schema_linking.schema_linking import SchemaLinking

logger = log.getLogger()


class DataAgentSchemaLinking(SchemaLinking):
    def __init__(self, model: EmbeddingModel, **kwargs):
        super().__init__(model, **kwargs)

    def search(
        self,
        question_embedding: str,
        batch_tables: list[str],
        table_embedding,
        columns_embedding,
        limit_score: int = 65,
        tok_k: int = 100,
    ) -> tuple[list[str], list[str]]:
        logger.debug("批处理相似性分值")
        batch_score = self.calc_similarity(question_embedding, table_embedding, columns_embedding)
        logger.debug("批处理相似性分值完成")
        return batch_tables, batch_score

    def calc_score(self, query_embedding, search_embedding):
        new_arr = np.zeros(
            [len(search_embedding), len(max(search_embedding, key=lambda x: len(x))), 1024]
        )
        for i, j in enumerate(search_embedding):
            new_arr[i][0 : len(j)] = j

        product = np.einsum("ijk,lk->ilj", new_arr, query_embedding)
        max_score = np.max(product, axis=2)
        return np.average(max_score, axis=1)

    def calc_similarity(self, query_embedding, table_embedding, columns_embedding, table_weight=30):
        if not table_embedding or not columns_embedding:
            return [0]
        table_embedding = [item[0] for item in table_embedding]
        columns_embedding = [item[0] for item in columns_embedding]
        similarity_table = self.calc_score(query_embedding, table_embedding)
        similarity_field = self.calc_score(query_embedding, columns_embedding)
        score = table_weight * similarity_table + similarity_field
        max_s, min_s = 1 * table_weight + 1, 0
        similarity = (score - min_s) / (max_s - min_s) * 100
        return similarity
