from enum import Enum

from pydantic import BaseModel


class ActionStatus(Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"


class ActionResultScope(Enum):
    user = "user"
    internal = "internal"


class ActionResult(BaseModel):
    scope: ActionResultScope
    result: dict
