from abc import ABC, abstractmethod
from dg_agent.config import Component


class LLM(Component, ABC):
    @abstractmethod
    async def generate_completion_stream(self, prompt: str, session_id: str, model_name: str):
        pass
