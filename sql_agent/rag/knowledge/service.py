import concurrent.futures
import logging

from overrides import override

from sql_agent.db import Storage
from sql_agent.db.repositories.knowledge import KnowledgeStorage
from sql_agent.db.repositories.sync_knowledge import KnowledgeSyncRepository
from sql_agent.db.repositories.types import Knowledge, KnowledgeEmbeddingStatus
from sql_agent.llm.embedding_model import EmbeddingModel
from sql_agent.rag import schema_linking
from sql_agent.rag.knowledge import KnowledgeService, process_single_doc
from sql_agent.rag.knowledge.types import Document
from sql_agent.setting import System

logger = logging.getLogger(__name__)

system = System()


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


class KnowledgeServiceImpl(KnowledgeService):
    embedding_model = EmbeddingModel()

    def __init__(self):
        super().__init__()
        self.embedding_model = EmbeddingModel()
        self.csv_file_suffix = "_knowledge.csv"
        self.storage = system.get_module(Storage)
        self.knowledge_repository = KnowledgeStorage(self.storage)
        self.knowledge_sync_repository = KnowledgeSyncRepository(self.storage)
        self.process_pool = system.get_process_pool()

    @override
    def query_doc(self, query_texts: str, source: list[str], num_results: int):
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
    def upload_doc(self, file_path: str, record_id: str) -> bool:
        logger.info(f"上传知识库文件:{file_path}")
        texts = process_single_doc(file_path)
        record = self.knowledge_sync_repository.find_by_id(record_id)
        if record.status == KnowledgeEmbeddingStatus.STOP.value:
            logger.info("已手动停止,上传终止")
            return False
        if texts:
            for text in texts:
                record = self.knowledge_sync_repository.find_by_id(record_id)
                if record.status == KnowledgeEmbeddingStatus.STOP.value:
                    logger.info("已手动停止,上传终止")
                    return False
                content_embedding = self.embedding_model.embed_query(text.page_content).tolist()
                knowledge = Knowledge(
                    source=file_path,
                    content=text.page_content,
                    content_embedding=content_embedding,
                )
                self.knowledge_repository.insert(knowledge)
        return True

    @override
    def delete_doc(self, condition: dict):
        self.knowledge_repository.delete_by(condition)

    @override
    def delete_doc_ids(self, ids: list[str]):
        pass
