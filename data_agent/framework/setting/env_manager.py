import os
from abc import ABC, abstractmethod
from typing import Any

from dotenv import load_dotenv


class Env(ABC):
    def __init__(self, path: str | None):
        load_dotenv(dotenv_path=path)
        self.init()
        pass

    @abstractmethod
    def init(self):
        pass

    def get(self, key: str) -> str:
        val = self[key]
        if val is None:
            raise ValueError(f"Missing required config value '{key}'")
        return val

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, "")
