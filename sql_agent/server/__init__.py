from abc import ABC, abstractmethod

from sql_agent.config import Settings


class Server(ABC):
    @abstractmethod
    def __init__(self, settings: Settings):
        pass
