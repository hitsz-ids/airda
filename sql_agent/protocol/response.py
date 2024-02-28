from typing import Any

from pydantic import BaseModel


class BaseResponse(BaseModel):
    msg: str
    code: int
    data: Any
