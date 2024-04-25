from abc import ABC, abstractmethod

from airda.server.protocol import ChatCompletionRequest


class API(ABC):
    @abstractmethod
    async def create_completion(self, request: ChatCompletionRequest):
        pass
