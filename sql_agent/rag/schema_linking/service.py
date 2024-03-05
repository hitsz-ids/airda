import heapq
import logging
import concurrent.futures
from typing import Any, Tuple

import numpy as np

import sql_agent
from sql_agent.rag.schema_linking import SchemaLinking
from sql_agent.setting import System
from sql_agent.db import Storage
from sql_agent.db.repositories.instructions import InstructionRepository
from sql_agent.llm.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)


system = System()


class SchemaLinkingImpl(SchemaLinking):

    def search(
        self, query: str, datasource_id: str, database: str, limit_score=65, top_k=100
    ) -> Tuple[list[str], list[str]]:
        logger.info("开始查询相似表")
        question_embedding = self._embedding_question(query)
        all_tables, all_scores = self._retrieve_db_embeddings(
            question_embedding, datasource_id, database
        )
        sorted_result = self._rank_tables(all_tables, all_scores, top_k)
        return self._filter_results(sorted_result, all_scores, limit_score)

    def _retrieve_db_embeddings(
        self, question_embedding, datasource_id: str, database: str
    ):
        page = 1
        limit = 5
        all_tables = []
        all_scores = []
        is_end = False
        instruction_repository = InstructionRepository(self.storage)
        tasks = []

        while not is_end:
            db_embedding = instruction_repository.find_embedding_by(
                {"datasource_id": str(datasource_id), "database": database},
                page=page,
                limit=limit,
            )
            logger.info(f"查询第{page}页数据,返回{len(db_embedding)}条数据")

            batch_tables = [item.table_name for item in db_embedding]
            task = sql_agent.config.process_pool.submit(
                do_calc_similarity, (batch_tables, question_embedding, db_embedding)
            )
            if len(db_embedding) == 0:
                break
            batch_tables = [item.table_name for item in db_embedding]
            task = sql_agent.config.process_pool.submit(
                do_calc_similarity,
                (batch_tables, question_embedding, db_embedding),
            )
            tasks.append(task)

            page += 1
            if len(db_embedding) < limit:
                is_end = True

        for future in concurrent.futures.as_completed(tasks):
            batch_tables, batch_score = future.result()
            all_tables.extend(batch_tables)
            all_scores.extend(batch_score)
        return all_tables, all_scores

    def _rank_tables(self, all_tables, all_scores, top_k):
        top_k_idxs = heapq.nlargest(
            top_k, range(len(all_scores)), key=all_scores.__getitem__
        )
        sorted_result = [all_tables[i] for i in top_k_idxs]
        return sorted_result

    def _embedding_question(self, question: str):
        return self.embedding_model.embed_query(question)[0]

    def _filter_results(self, sorted_result, all_scores, limit_score):
        limit_score_idxs = [
            idx for idx, sim in enumerate(all_scores) if sim > limit_score
        ]
        limit_score_len = len(limit_score_idxs)
        max_length = 10
        if limit_score_len > max_length:
            limit_score_len = max_length
        top_result_num = 5
        return sorted_result[:limit_score_len], sorted_result[:top_result_num]


def calc_score(query_embedding, search_embedding):
    new_arr = np.zeros(
        [len(search_embedding), len(max(search_embedding, key=lambda x: len(x))), 1024]
    )
    for i, j in enumerate(search_embedding):
        new_arr[i][0 : len(j)] = j

    product = np.einsum("ijk,lk->ilj", new_arr, query_embedding)
    max_score = np.max(product, axis=2)
    return np.average(max_score, axis=1)


def calc_similarity(
    query_embedding, table_embedding, columns_embedding, table_weight=30
):
    if not table_embedding or not columns_embedding:
        return [0]
    table_embedding = [item[0] for item in table_embedding]
    columns_embedding = [item[0] for item in columns_embedding]
    similarity_table = calc_score(query_embedding, table_embedding)
    similarity_field = calc_score(query_embedding, columns_embedding)
    score = table_weight * similarity_table + similarity_field
    max_s, min_s = 1 * table_weight + 1, 0
    similarity = (score - min_s) / (max_s - min_s) * 100
    return similarity


def do_calc_similarity(args):
    logger.info("批处理相似性分值")
    batch_tables, question_embedding, db_embedding = args
    table_embedding = [item.table_comment_embedding for item in db_embedding]
    columns_embedding = [item.column_embedding for item in db_embedding]
    batch_score = calc_similarity(
        question_embedding, table_embedding, columns_embedding
    )
    logger.info("批处理相似性分值完成")
    return batch_tables, batch_score
