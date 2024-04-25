from typing import List

from airda.agent import log
from airda.agent.storage.entity.datasource import Datasource
from airda.agent.storage.repositories.respository import Repository

DB_COLLECTION = "datasource"

logger = log.getLogger()


class DatasourceRepository(Repository):
    def add(self, datasource: Datasource) -> Datasource:
        has = self.find_one(datasource.name)
        if has:
            raise Exception("datasource already exists")
        datasource_dict = datasource.dict(exclude={"id"})
        datasource.id = str(self.storage.insert_one(DB_COLLECTION, datasource_dict))
        return datasource

    def ls(self) -> List[Datasource]:
        _list = self.storage.find_all(DB_COLLECTION)
        result = []
        if _list:
            for datasource in _list:
                result.append(
                    Datasource(
                        id=str(datasource["_id"]),
                        name=datasource["name"],
                        host=datasource["host"],
                        port=datasource["port"],
                        kind=datasource["kind"],
                        database=datasource["database"],
                        username=datasource["username"],
                        password=datasource["password"],
                        enable=datasource["enable"],
                    ),
                )
        return result

    def enable(self, name: str) -> bool:
        _list = self.storage.find(DB_COLLECTION, {"enable": True})
        if _list:
            for item in _list:
                item["enable"] = False
                self.storage.update(DB_COLLECTION, {"name": name}, item)
        datasource = self.storage.find_one(DB_COLLECTION, {"name": name})
        if datasource is None:
            logger.error("未找到[{}]的数据源".format(name))
            return False
        datasource["enable"] = True
        self.storage.update(DB_COLLECTION, {"name": name}, datasource)
        return True

    def disable(self, name: str) -> bool:
        datasource = self.storage.find_one(DB_COLLECTION, {"name": name})
        if datasource is None:
            logger.error("未找到[{}]的数据源".format(name))
            return False
        datasource["enable"] = False
        self.storage.update(DB_COLLECTION, {"name": name}, datasource)
        return True

    def delete(self, name: str):
        self.storage.delete_by(DB_COLLECTION, {"name": name})

    def find_enable(self) -> Datasource:
        datasource = self.storage.find_one(DB_COLLECTION, {"enable": True})
        return DatasourceRepository.get_datasource(datasource)

    def find_one(self, name: str) -> Datasource | None:
        datasource = self.storage.find_one(DB_COLLECTION, {"name": name})
        return DatasourceRepository.get_datasource(datasource)

    @staticmethod
    def get_datasource(datasource: dict) -> Datasource | None:
        if datasource is None:
            return None
        return Datasource(
            id=str(datasource["_id"]),
            name=datasource["name"],
            host=datasource["host"],
            port=datasource["port"],
            kind=datasource["kind"],
            database=datasource["database"],
            username=datasource["username"],
            password=datasource["password"],
            enable=datasource["enable"],
        )
