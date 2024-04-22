from enum import Enum


class TableDescriptionStatus(Enum):
    NOT_SYNCHRONIZED = "NOT_SYNCHRONIZED"
    SYNCHRONIZING = "SYNCHRONIZING"
    DEPRECATED = "DEPRECATED"
    SYNCHRONIZED = "SYNCHRONIZED"
    FAILED = "FAILED"


class DBEmbeddingStatus(Enum):
    EMBEDDING = 1
    SUCCESS = 2
    FAILED = 3
    STOP = 4
