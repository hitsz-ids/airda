from abc import ABC, abstractmethod
from typing import List

from dg_agent.config import Component, System


class DocIndex(Component, ABC):
    collections: List[str]

    @abstractmethod
    def __init__(self, system: System):
        self.system = system

    @abstractmethod
    def query_doc(self, query_texts: str,
                  source: List[str],
                  collection: str,
                  num_results: int):
        pass

    @abstractmethod
    def upload_doc(self,
                   file_path: str,
                   collection: str):
        pass

    @abstractmethod
    def delete_doc(self, ids: List[str],
                   collection: str):
        pass
