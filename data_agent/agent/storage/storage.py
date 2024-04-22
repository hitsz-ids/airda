from typing import Any, Iterable, TypeVar, Union

from bson import ObjectId
from bson.raw_bson import RawBSONDocument
from pymongo import MongoClient
from pymongo.database import Database

from data_agent.agent.env import DataAgentEnv
from data_agent.agent.storage import StorageKey
from data_agent.agent.storage.repositories.datasource_repository import (
    DatasourceRepository,
)
from data_agent.agent.storage.repositories.instruction_repository import (
    InstructionRepository,
)
from data_agent.framework.agent.context import Context
from data_agent.framework.agent.module.loader import Loader
from data_agent.framework.module.keys import Keys

T = TypeVar("T")


class DataAgentStorage(Loader):
    database: Database
    client: MongoClient

    def __init__(self, context: Context):
        super().__init__(context)
        self.init_storage()
        super().load(StorageKey.INSTRUCTION, InstructionRepository)
        super().load(StorageKey.DATASOURCE, DatasourceRepository)

    def init_storage(self):
        uri = DataAgentEnv().mongodb_uri
        db_name = DataAgentEnv().mongodb_db_name
        username = DataAgentEnv().mongodb_username
        password = DataAgentEnv().mongodb_password
        if username and password:
            self.client = MongoClient(uri, username=username, password=password)
            self.database = self.client[db_name]
        else:
            self.client = MongoClient(uri)
            self.database = self.client[db_name]

    def find_one(self, collection: str, query: dict) -> dict:
        return self.database[collection].find_one(query)

    def insert_one(self, collection: str, obj: dict) -> int:
        return self.database[collection].insert_one(obj).inserted_id

    def insert_many(self, collection: str, obj: Iterable[Union[Any, RawBSONDocument]]) -> list:
        return self.database[collection].insert_many(obj).inserted_ids

    def rename(self, old_collection_name: str, new_collection_name) -> None:
        self.database[old_collection_name].rename(new_collection_name)

    def rename_field(self, collection_name: str, old_field_name: str, new_field_name: str) -> None:
        self.database[collection_name].update_many(
            {}, {"$rename": {old_field_name: new_field_name}}
        )

    def update_or_create(self, collection: str, query: dict, obj: dict) -> int:
        row = self.find_one(collection, query)
        if row:
            self.database[collection].update_one(query, {"$set": obj})
            return row["_id"]
        return self.insert_one(collection, obj)

    def update(self, collection: str, query: dict, obj: dict) -> int:
        row = self.find_one(collection, query)
        if row:
            self.database[collection].update_one(query, {"$set": obj})
            return row["_id"]

    def find_by_id(self, collection: str, id: str) -> dict:
        return self.database[collection].find_one({"_id": ObjectId(id)})

    def find(
        self,
        collection: str,
        query: dict,
        sort: list = None,
        page: int = 0,
        limit: int = 0,
    ) -> list:
        skip_count = (page - 1) * limit
        cursor = self.database[collection].find(query)
        if sort:
            cursor = cursor.sort(sort)
        if page > 0 and limit > 0:
            cursor = cursor.skip(skip_count).limit(limit)
        return list(cursor)

    def find_all(self, collection: str, page: int = 0, limit: int = 0) -> list:
        if page > 0 and limit > 0:
            skip_count = (page - 1) * limit
            return list(self.database[collection].find({}).skip(skip_count).limit(limit))
        return list(self.database[collection].find({}))

    def delete_by_id(self, collection: str, id: str) -> int:
        result = self.database[collection].delete_one({"_id": ObjectId(id)})
        return result.deleted_count

    def delete_by(self, collection: str, query: dict) -> int:
        result = self.database[collection].delete_many(query)
        return result.deleted_count

    def get_repositories(self, storage_key: Keys):
        if storage_key == StorageKey.INSTRUCTION:
            return super().get_lazy(storage_key, InstructionRepository)(self)
        if storage_key == StorageKey.DATASOURCE:
            return super().get_lazy(storage_key, DatasourceRepository)(self)

    def start_session(self):
        return self.client.start_session()
