import concurrent.futures
import logging
from typing import List

from overrides import override

from sql_agent import setting
from sql_agent.setting import System
from sql_agent.db import DB
from sql_agent.db.repositories.knowledge import KnowledgeRepository
from sql_agent.db.repositories.types import Knowledge
from sql_agent.llm.embedding_model import EmbeddingModel
from sql_agent.rag import schema_linking
from sql_agent.rag.knowledge import KnowledgeDocIndex, process_single_doc
from sql_agent.rag.knowledge.types import Document

logger = logging.getLogger(__name__)


def calculate_similarity(args):
    query_embedding, knowledge_list = args
    knowledge_result = []
    for knowledge_item in knowledge_list:
        score = schema_linking.calc_score(query_embedding, knowledge_item.content_embedding)
        knowledge_score = {
            "id": knowledge_item.id,
            "score": score,
            "content": knowledge_item.content,
        }
        knowledge_result.append(knowledge_score)
    return knowledge_result


class MongoDoc(KnowledgeDocIndex):
    embedding_model = EmbeddingModel()

    def __init__(self, system: System):
        super().__init__(system)
        self.embedding_model = EmbeddingModel()
        self.csv_file_suffix = "_knowledge.csv"
        self.knowledge_repository = KnowledgeRepository(system.get_instance(DB))
        self.process_pool = config.process_pool

    @override
    def query_doc(self, query_texts: str, source: List[str], collection: str, num_results: int):
        query_condition = {}
        if source:
            query_condition = {"source": {"$in": source}}
        page = 1
        page_size = 20
        query_embedding = self.embedding_model.embed_query(query_texts)[0]
        futures = []
        while page_size == 20:
            result = self.knowledge_repository.find_by(query_condition, page=page, limit=page_size)
            task = self.process_pool.submit(calculate_similarity, (query_embedding, result))
            futures.append(task)
            page_size = len(result)
            page += 1
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        docs = []
        if results:
            knowledge_score_list = []
            for result in results:
                if result:
                    knowledge_score_list.extend(result)
            knowledge_score_list = sorted(
                knowledge_score_list, key=lambda x: x["score"], reverse=True
            )
            top_score_list = knowledge_score_list[:num_results]
            docs = []
            for score_item in top_score_list:
                content = score_item["content"].replace("knowledge: ", "")
                score = score_item["score"]
                logger.info(f"知识/指标: {content},相似分值为: {score}")
                docs.append(Document(page_content=content, score=score))
        return docs

    @override
    def upload_doc(self, file_path: str, collection: str):
        logger.info(f"上传知识库文件:{file_path}")
        texts = process_single_doc(file_path)
        if texts:
            for text in texts:
                content_embedding = self.embedding_model.embed_query(text.page_content).tolist()
                knowledge = Knowledge(
                    source=file_path, content=text.page_content, content_embedding=content_embedding
                )
                self.knowledge_repository.insert(knowledge)

    @override
    def delete_doc(self, condition: dict):
        self.knowledge_repository.delete_by(condition)

    @override
    def delete_doc_ids(self, ids: List[str], collection: str):
        pass
