import os
from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from sql_agent.config import Component, System
from sql_agent.db import DB
from sql_agent.protocol.types import GoldenRecord, Question
from sql_agent.vector_store import VectorStore


class ContextStore(Component, ABC):
    DocStore: DB
    VectorStore: VectorStore
    doc_store_collection = "table_meta_data"

    @abstractmethod
    def __init__(self, system: System):
        self.system = system
        self.db = self.system.instance(DB)
        self.golden_record_collection = os.environ.get(
            "GOLDEN_RECORD_COLLECTION", "sql_agent-staging"
        )
        self.vector_store = self.system.instance(VectorStore)

    @abstractmethod
    def retrieve_context_for_question(
            self, nl_question: Question, number_of_samples: int = 3
    ) -> Tuple[Union[List[dict], None], Union[List[dict], None]]:
        pass

    @abstractmethod
    def add_golden_records(
            self, golden_records: List[GoldenRecord]
    ):
        pass

    @abstractmethod
    def get_golden_records(
            self, nl_question: Question, number_of_samples: int = 3
    ):
        pass

    @abstractmethod
    def remove_golden_records(self, ids: List) -> bool:
        pass
