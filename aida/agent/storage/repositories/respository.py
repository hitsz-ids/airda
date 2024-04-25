from abc import ABC
from typing import TYPE_CHECKING

from aida.framework.module.lazy import Lazy

if TYPE_CHECKING:
    from agent.storage.storage import DataAgentStorage


class Repository(Lazy, ABC):
    storage: "DataAgentStorage"

    def __init__(self, storage):
        super().__init__()
        self.storage = storage

    def submit(self, func, *args):
        session = self.storage.start_session()
        try:
            func(*args)
            session.commit_transaction()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.end_session()
