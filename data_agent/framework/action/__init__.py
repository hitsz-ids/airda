from enum import Enum


class ActionStatus(Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"


class ActionResultScope(Enum):
    USER = "USER"
    INTERNAL = "INTERNAL"
