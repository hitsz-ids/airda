from abc import ABC, abstractmethod

from fastapi import BackgroundTasks

from sql_agent.setting import BaseModule
from sql_agent.protocol import (
    ChatCompletionRequest,
    CompletionInstructionSyncRequest,
    CompletionKnowledgeLoadRequest,
    DatasourceAddRequest,
)


class API(BaseModule, ABC):
    @abstractmethod
    async def create_completion(self, request: ChatCompletionRequest):
        pass

    @abstractmethod
    async def datasource_add(self, request: DatasourceAddRequest):
        pass

    @abstractmethod
    async def instruction_sync(
        self,
        request: CompletionInstructionSyncRequest,
        background_tasks: BackgroundTasks,
    ):
        pass

    @abstractmethod
    async def knowledge_train(
        self, request: CompletionKnowledgeLoadRequest, background_tasks: BackgroundTasks
    ):
        pass
