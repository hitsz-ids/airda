from abc import ABC, abstractmethod

from data_agent.server.protocol import ChatCompletionRequest


class API(ABC):
    @abstractmethod
    async def create_completion(self, request: ChatCompletionRequest):
        pass
