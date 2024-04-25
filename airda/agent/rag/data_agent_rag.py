import heapq

from airda.agent import log
from airda.agent.process_pool.DataAgentProcessPool import DataAgentProcessPool
from airda.agent.rag.embedding.data_agent_embedding_model import (
    DataAgentEmbeddingModel,
)
from airda.agent.rag.schema_linking.data_agent_schema_linking import (
    DataAgentSchemaLinking,
)
from airda.agent.storage import StorageKey
from airda.agent.storage.repositories.instruction_repository import (
    InstructionRepository,
)
from airda.framework.agent.module.rag.rag import Rag

logger = log.getLogger()


class DataAgentRag(Rag):
    def init_embedding(self) -> type[DataAgentEmbeddingModel]:
        return DataAgentEmbeddingModel

    def init_schema_linking(self) -> type[DataAgentSchemaLinking]:
        return DataAgentSchemaLinking

    def search(
        self,
        question,
        datasource_id: str | int,
        database: str,
        limit_score: int = 65,
        top_k: int = 100,
    ) -> tuple[list[str], list[str]]:
        all_tables, all_scores = self._retrieve_db_embeddings(
            question, datasource_id, database, limit_score, top_k
        )
        sorted_result = self._rank_tables(all_tables, all_scores, top_k)
        return self._filter_results(sorted_result, all_scores, limit_score)

    def _retrieve_db_embeddings(
        self,
        question,
        datasource_id: str | int,
        database: str,
        limit_score: int = 65,
        tok_k: int = 100,
    ):
        page = 1
        limit = 5
        all_tables = []
        all_scores = []
        is_end = False
        tasks = []
        from airda.agent.data_agent_context import DataAgentContext

        context = self.context.convert(DataAgentContext)
        instruction_repository = context.get_repository(StorageKey.INSTRUCTION).convert(
            InstructionRepository
        )
        schema_linking = super().get_schema_linking()
        question_embedding = self.get_embedding_model().embed_query(question)[0]
        while not is_end:
            instructions = instruction_repository.find_by(
                {"datasource_id": datasource_id, "database": database},
                page=page,
                limit=limit,
            )
            logger.debug(f"查询第{page}页数据,返回{len(instructions)}条数据")
            if len(instructions) == 0:
                break
            batch_tables = [item.table_name for item in instructions]
            table_embedding = [item.table_comment_embedding for item in instructions]
            columns_embedding = [item.table_column_embedding for item in instructions]
            task = DataAgentProcessPool().submit(
                schema_linking.search,
                question_embedding,
                batch_tables,
                table_embedding,
                columns_embedding,
                limit_score,
                tok_k,
            )
            tasks.append(task)

            page += 1
            if len(instructions) < limit:
                is_end = True
        for future in DataAgentProcessPool().as_completed(tasks):
            batch_tables, batch_score = future.result()
            all_tables.extend(batch_tables)
            all_scores.extend(batch_score)
        return all_tables, all_scores

    def _rank_tables(self, all_tables, all_scores, top_k: int = 100):
        top_k_idxs = heapq.nlargest(top_k, range(len(all_scores)), key=all_scores.__getitem__)
        sorted_result = [all_tables[i] for i in top_k_idxs]
        return sorted_result

    def _filter_results(self, sorted_result, all_scores, limit_score):
        limit_score_idxs = [idx for idx, sim in enumerate(all_scores) if sim > limit_score]
        limit_score_len = len(limit_score_idxs)
        max_length = 10
        if limit_score_len > max_length:
            limit_score_len = max_length
        top_result_num = 5
        return sorted_result[:limit_score_len], sorted_result[:top_result_num]
