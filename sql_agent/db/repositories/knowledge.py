from bson.objectid import ObjectId

from sql_agent.db.repositories.types import Knowledge

KNOWLEDGE_EMBEDDING_COLLECTION = "knowledge_embedding"


class KnowledgeRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, knowledge_embedding: Knowledge) -> Knowledge:
        embedding_record_dict = knowledge_embedding.dict(exclude={"id"})
        Knowledge.id = str(
            self.storage.insert_one(KNOWLEDGE_EMBEDDING_COLLECTION, embedding_record_dict)
        )
        return knowledge_embedding

    def find_one(self, query: dict) -> Knowledge | None:
        row = self.storage.find_one(KNOWLEDGE_EMBEDDING_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["source"] = str(row["source"])
        return Knowledge(**row)

    def find_by(self, query: dict, page: int = 1, limit: int = 10) -> list[Knowledge]:
        rows = self.storage.find(KNOWLEDGE_EMBEDDING_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            result.append(Knowledge(**row))
        return result

    def update(self, knowledge_embedding: Knowledge) -> Knowledge:
        embedding_record_dict = knowledge_embedding.dict(exclude={"id"})
        embedding_record_dict["source"] = knowledge_embedding.source

        self.storage.update_or_create(
            KNOWLEDGE_EMBEDDING_COLLECTION,
            {"_id": ObjectId(knowledge_embedding.id)},
            embedding_record_dict,
        )
        return knowledge_embedding

    def delete_by(self, query: dict) -> int:
        return self.storage.delete_by(KNOWLEDGE_EMBEDDING_COLLECTION, query)
