from enum import Enum

from pydantic import BaseModel


class Kind(Enum):
    MYSQL = "MYSQL"

    @staticmethod
    def getKind(name: str) -> str | None:
        name = name.lower()
        if name == Kind.MYSQL.value.lower():
            return Kind.MYSQL.value
        return None


class Datasource(BaseModel):
    id: str | None = None
    name: str
    host: str
    port: int
    kind: str
    database: str
    username: str | None = None
    password: str | None = None
    enable: bool | None = False
