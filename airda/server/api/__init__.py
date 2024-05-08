from abc import ABC, abstractmethod

from airda.server.protocol import AddDatasourceRequest, ChatCompletionRequest


class API(ABC):
    @abstractmethod
    async def create_completion(self, request: ChatCompletionRequest):
        pass

    @abstractmethod
    async def add_datasource(self, request: AddDatasourceRequest):
        pass
