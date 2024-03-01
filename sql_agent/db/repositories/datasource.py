from bson.objectid import ObjectId

from sql_agent.db.repositories.types import Datasource

DATASOURCE_COLLECTION = "datasource"


class DatasourceRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, datasource: Datasource) -> Datasource:
        datasource_dict = datasource.dict(exclude={"id"})
        datasource.id = str(self.storage.insert_one(DATASOURCE_COLLECTION, datasource_dict))
        return datasource

    def update(self, datasource: Datasource) -> Datasource:
        datasource_dict = datasource.dict(exclude={"id", "type"})
        self.storage.update_or_create(
            DATASOURCE_COLLECTION,
            {"_id": ObjectId(datasource.id)},
            datasource_dict,
        )
        return datasource

    def find_by_id(self, id: str) -> Datasource | None:
        row = self.storage.find_one(DATASOURCE_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        return Datasource(**row)

    def delete_by_id(self, id: str) -> int:
        return self.storage.delete_by_id(DATASOURCE_COLLECTION, id)
