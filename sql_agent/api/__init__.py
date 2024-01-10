from abc import ABC, abstractmethod

from fastapi import BackgroundTasks

from sql_agent.config import Component
from sql_agent.protocol import (
    ChatCompletionRequest,
    CompletionKnowledgeLoadRequest,
    CompletionKnowledgeDeleteRequest,
    CompletionGoldenSQLAddRequest
)


class API(Component, ABC):
    @abstractmethod
    async def create_completion(self, request: ChatCompletionRequest):
        pass

    @abstractmethod
    async def knowledge_train(self, request: CompletionKnowledgeLoadRequest, background_tasks: BackgroundTasks):
        pass

    @abstractmethod
    async def delete_knowledge_file(self, request: CompletionKnowledgeDeleteRequest):
        pass

    @abstractmethod
    def add_golden_sql(self, request: CompletionGoldenSQLAddRequest):
        pass
