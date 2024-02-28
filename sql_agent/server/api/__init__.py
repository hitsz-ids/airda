from abc import ABC, abstractmethod

from starlette.background import BackgroundTasks

from sql_agent.protocol import (
    ChatCompletionRequest,
    CompletionInstructionSyncRequest,
    CompletionKnowledgeLoadRequest,
    DatasourceAddRequest,
)


class API(ABC):
    @abstractmethod
    async def create_completion(self, request: ChatCompletionRequest):
        pass

    @abstractmethod
    async def datasource_add(self, request: DatasourceAddRequest):
        pass

    @abstractmethod
    async def instruction_sync(
        self, request: CompletionInstructionSyncRequest, background_tasks: BackgroundTasks
    ):
        pass

    @abstractmethod
    async def knowledge_train(
        self, request: CompletionKnowledgeLoadRequest, background_tasks: BackgroundTasks
    ):
        pass
