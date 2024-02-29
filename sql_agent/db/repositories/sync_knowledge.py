from typing import Union

from bson.objectid import ObjectId

from sql_agent.db.repositories.types import InstructionEmbeddingRecord as EmbeddingRecord

SYNC_EMBEDDING_COLLECTION = "sync_datasource"


class KnowledgeSyncRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, embedding_record: EmbeddingRecord) -> EmbeddingRecord:
        embedding_record_dict = embedding_record.dict(exclude={"id"})
        embedding_record_dict["db_connection_id"] = embedding_record.datasource_id
        embedding_record.id = str(
            self.storage.insert_one(SYNC_EMBEDDING_COLLECTION, embedding_record_dict)
        )
        return embedding_record

    def find_one(self, query: dict) -> Union[EmbeddingRecord, None]:
        row = self.storage.find_one(SYNC_EMBEDDING_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return EmbeddingRecord(**row)

    def update(self, embedding_record: EmbeddingRecord) -> EmbeddingRecord:
        embedding_record_dict = embedding_record.dict(exclude={"id"})
        embedding_record_dict["db_connection_id"] = embedding_record.db_connection_id

        self.storage.update_or_create(
            SYNC_EMBEDDING_COLLECTION,
            {"_id": ObjectId(embedding_record.id)},
            embedding_record_dict,
        )
        return embedding_record
