from bson import ObjectId

from data_agent.agent import log
from data_agent.agent.storage.entity.instruction import Instruction
from data_agent.agent.storage.repositories.respository import Repository

DB_COLLECTION = "instructions"

logger = log.getLogger()


class InstructionRepository(Repository):
    def insert(self, instruction: Instruction) -> Instruction:
        instruction_dict = instruction.dict(exclude={"id"})
        instruction_dict["datasource_id"] = instruction.datasource_id
        instruction.id = str(self.storage.insert_one(DB_COLLECTION, instruction_dict))
        return instruction

    def find_one(self, query: dict) -> Instruction | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        return Instruction(**row)

    def update(self, instruction: Instruction) -> Instruction:
        instruction_dict = instruction.dict(exclude={"id"})
        instruction_dict["datasource_id"] = instruction.datasource_id

        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(instruction.id)},
            instruction_dict,
        )
        return instruction

    def find_by_id(self, id: str) -> Instruction | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        return Instruction(**row)

    def find_by(self, query: dict, page: int = 1, limit: int = 10) -> list[Instruction]:
        rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            result.append(Instruction(**row))
        return result

    def find_all(self, page: int = 0, limit: int = 0) -> list[Instruction]:
        rows = self.storage.find_all(DB_COLLECTION, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            result.append(Instruction(**row))
        return result

    def delete_by_id(self, id: str) -> int:
        return self.storage.delete_by_id(DB_COLLECTION, id)

    def delete_by(self, query: dict) -> int:
        return self.storage.delete_by(DB_COLLECTION, query)

    def delete(self, datasource_id: str, database: str):
        return self.storage.delete_by(
            DB_COLLECTION, {"datasource_id": datasource_id, "database": database}
        )
