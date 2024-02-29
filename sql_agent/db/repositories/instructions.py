from typing import Union

from bson.objectid import ObjectId

from sql_agent.db.repositories.types import Instruction, EmbeddingInstruction

DB_COLLECTION = "instructions"

DB_EMBEDDING_COLLECTION = "instructions_embedding"


class InstructionRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, instruction: Instruction) -> Instruction:
        instruction_dict = instruction.dict(exclude={"id"})
        instruction_dict["db_connection_id"] = ObjectId(instruction.db_connection_id)
        instruction.id = str(self.storage.insert_one(DB_COLLECTION, instruction_dict))

        return instruction

    def find_one(self, query: dict) -> Union[Instruction, None]:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return Instruction(**row)

    def update(self, instruction: Instruction) -> Instruction:
        instruction_dict = instruction.dict(exclude={"id"})
        instruction_dict["db_connection_id"] = ObjectId(instruction.db_connection_id)

        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(instruction.id)},
            instruction_dict,
        )
        return instruction

    def find_by_id(self, id: str) -> Union[Instruction, None]:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return Instruction(**row)

    def find_by(self, query: dict, page: int = 1, limit: int = 10) -> list[Instruction]:
        rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            result.append(Instruction(**row))
        return result

    def find_all(self, page: int = 0, limit: int = 0) -> list[Instruction]:
        rows = self.storage.find_all(DB_COLLECTION, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            result.append(Instruction(**row))
        return result

    def delete_by_id(self, id: str) -> int:
        return self.storage.delete_by_id(DB_COLLECTION, id)

    def insert_embedding(self, embedding_instruction: EmbeddingInstruction):
        instruction_dict = embedding_instruction.dict(exclude={"id"})
        self.storage.insert_one(DB_EMBEDDING_COLLECTION, instruction_dict)

    def find_one_embedding(self, query: dict):
        row = self.storage.find_one(DB_EMBEDDING_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return EmbeddingInstruction(**row)

    def find_embedding_by(
        self, query: dict, page: int = 1, limit: int = 10
    ) -> list[EmbeddingInstruction]:
        rows = self.storage.find(DB_EMBEDDING_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            result.append(EmbeddingInstruction(**row))
        return result

    def delete_embedding_by(self, query: dict) -> int:
        return self.storage.delete_by(DB_EMBEDDING_COLLECTION, query)
