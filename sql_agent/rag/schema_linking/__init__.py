import concurrent.futures
import heapq
import logging
from typing import List, Tuple

import numpy as np

import sql_agent
from sql_agent.config import System
from sql_agent.db import DB
from sql_agent.db.repositories.instructions import InstructionRepository
from sql_agent.llm.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)

TABLE_PREFIX = "tableSchemaDetails-"


def calc_score(query_embedding, search_embedding):
    narry = np.zeros(
        [len(search_embedding), len(max(search_embedding, key=lambda x: len(x))), 1024]
    )
    for i, j in enumerate(search_embedding):
        narry[i][0 : len(j)] = j

    product = np.einsum("ijk,lk->ilj", narry, query_embedding)
    max_score = np.max(product, axis=2)
    return np.average(max_score, axis=1)


def calc_similarity(query_embedding, table_embedding, columns_embedding, table_weight=30):
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
    batch_score = calc_similarity(question_embedding, table_embedding, columns_embedding)
    logger.info("批处理相似性分值完成")
    return batch_tables, batch_score


class SchemaLinking:
    embedding_model = ""

    def __init__(self, system: System):
        self.system = system
        self.storage = self.system.instance(DB)
        self.embedding_model = EmbeddingModel()

    def get_similarity_table_names(
        self, question: str, db_connection_id: str, database: str
    ) -> Tuple[List[str], List[str]]:
        logger.info("开始查询相似表")
        question_embedding = self.embedding_model.embed_query(question)[0]
        page = 1
        limit = 5
        all_tables = []
        all_score = []
        is_end = False
        instruction_repository = InstructionRepository(self.storage)
        tasks = []
        while not is_end:
            logger.info(f"查询第{page}页数据")
            db_embedding = instruction_repository.find_embedding_by(
                {"db_connection_id": str(db_connection_id), "database": database},
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
            page += 1
            tasks.append(task)
            if len(db_embedding) < limit:
                is_end = True

        results = [future.result() for future in concurrent.futures.as_completed(tasks)]
        for result in results:
            batch_tables, batch_score = result
            all_tables.extend(batch_tables)
            all_score.extend(batch_score)

        # 过滤出分数 大于 limit_score 的条数
        limit_score = 65
        limit_score_idxs = [idx for idx, sim in enumerate(all_score) if sim > limit_score]
        limit_score_len = len(limit_score_idxs)

        # 获取排名前100的数据表index
        top_k = 100
        top_k_idxs = heapq.nlargest(top_k, range(len(all_score)), key=all_score.__getitem__)

        sorted_result = []
        top_result_num = 5
        logger.info(f"排名前「{top_k}」的数据表:")
        for idx, table_index in enumerate(top_k_idxs):
            table_name = all_tables[table_index]
            sorted_result.append(table_name)
            logger.info(f"表名：{table_name},相似性得分：{all_score[table_index]}，排名：{idx + 1}")

        max_length = 10
        if limit_score_len >= max_length:
            limit_score_len = max_length
        logger.info(f"超出阈值「{limit_score}」的数据表查询结果:")
        for idx, table_index in enumerate(top_k_idxs[:limit_score_len]):
            logger.info(f"表名：{all_tables[table_index]},相似性得分：{all_score[table_index]}，排名：{idx + 1}")
        return sorted_result[:limit_score_len], sorted_result[:top_result_num]
