from abc import ABC, abstractmethod

from starlette.background import BackgroundTasks

from sql_agent.protocol import (
    ChatCompletionRequest,
    CompletionInstructionSyncRequest,
    CompletionInstructionSyncStatusRequest,
    CompletionInstructionSyncStopRequest,
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
    async def instruction_sync(self, request: CompletionInstructionSyncRequest):
        pass

    @abstractmethod
    async def instruction_sync_status(self, request: CompletionInstructionSyncStatusRequest):
        pass

    @abstractmethod
    async def instruction_sync_stop(self, request: CompletionInstructionSyncStopRequest):
        pass

    @abstractmethod
    async def knowledge_train(
        self, request: CompletionKnowledgeLoadRequest, background_tasks: BackgroundTasks
    ):
        pass
