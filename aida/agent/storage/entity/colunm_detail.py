from pydantic import BaseModel


class ColumnDetail(BaseModel):
    name: str
    description: str = ""
