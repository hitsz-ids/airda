import fastapi
from fastapi import BackgroundTasks, Depends, File, Form, UploadFile
from overrides import overrides

from sql_agent.framework.server import WebFrameworkServer
from sql_agent.protocol import (
    ChatCompletionRequest,
    CompletionInstructionSyncRequest,
    CompletionInstructionSyncStatusRequest,
    CompletionInstructionSyncStopRequest,
    CompletionKnowledgeLoadRequest,
    CompletionKnowledgeStatusRequest,
    CompletionKnowledgeStopRequest,
    DatasourceAddRequest,
    DatasourceDeleteRequest,
    DatasourceUpdateRequest,
)


async def upload_file_form(
    file: UploadFile = File(...), file_id: str = Form(...), file_name: str = Form(...)
):
    return CompletionKnowledgeLoadRequest(file=file, file_id=file_id, file_name=file_name)


class SQLAgentServer(WebFrameworkServer):
    def __init__(self, host="0.0.0.0", port=8888):
        super().__init__(host, port)
        self.router = None

    @overrides
    def create_app(self):
        return fastapi.FastAPI(debug=True)

    @overrides
    def run_server(self):
        import uvicorn

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level=self.settings.get("log_level"),
        )

    @overrides
    def add_routes(self):
        self.router = fastapi.APIRouter()
        self.router.add_api_route(
            "/v1/chat/completions",
            self.create_completion,
            methods=["POST"],
            tags=["chat completions"],
        )

        self.router.add_api_route(
            "/v1/datasource/add",
            self.datasource_add,
            methods=["POST"],
            tags=["add datasource"],
        )

        self.router.add_api_route(
            "/v1/datasource/update",
            self.datasource_update,
            methods=["POST"],
            tags=["update datasource"],
        )

        self.router.add_api_route(
            "/v1/datasource/delete",
            self.datasource_delete,
            methods=["POST"],
            tags=["delete datasource"],
        )

        self.router.add_api_route(
            "/v1/instruction/sync",
            self.instruction_sync,
            methods=["POST"],
            tags=["instruction sync"],
        )

        self.router.add_api_route(
            "/v1/instruction/status",
            self.instruction_sync_status,
            methods=["GET"],
            tags=["instruction status"],
        )

        self.router.add_api_route(
            "/v1/instruction/stop",
            self.instruction_sync_stop,
            methods=["POST"],
            tags=["instruction stop"],
        )

        self.router.add_api_route(
            "/v1/knowledge/train",
            self.knowledge_train,
            methods=["POST"],
            tags=["knowledge train"],
        )

        self.router.add_api_route(
            "/v1/knowledge/status",
            self.knowledge_train_status,
            methods=["GET"],
            tags=["knowledge status"],
        )

        self.router.add_api_route(
            "/v1/knowledge/stop",
            self.knowledge_train_stop,
            methods=["POST"],
            tags=["knowledge stop"],
        )

        self.app.include_router(self.router)

    async def create_completion(self, request: ChatCompletionRequest):
        return await self._api.create_completion(request)

    async def instruction_sync(
        self,
        request: CompletionInstructionSyncRequest,
        background_tasks: BackgroundTasks,
    ):
        return await self._api.instruction_sync(request, background_tasks)

    async def instruction_sync_status(self, request: CompletionInstructionSyncStatusRequest):
        return await self._api.instruction_sync_status(request)

    async def instruction_sync_stop(self, request: CompletionInstructionSyncStopRequest):
        return await self._api.instruction_sync_stop(request)

    async def datasource_add(self, request: DatasourceAddRequest):
        return await self._api.datasource_add(request)

    async def datasource_update(self, request: DatasourceUpdateRequest):
        return await self._api.datasource_update(request)

    async def datasource_delete(self, request: DatasourceDeleteRequest):
        return await self._api.datasource_delete(request)

    async def knowledge_train(
        self,
        background_tasks: BackgroundTasks,
        request: CompletionKnowledgeLoadRequest = Depends(upload_file_form),
    ):
        return await self._api.knowledge_train(request, background_tasks)

    async def knowledge_train_status(self, request: CompletionKnowledgeStatusRequest):
        return await self._api.knowledge_train_status(request)

    async def knowledge_train_stop(self, request: CompletionKnowledgeStopRequest):
        return await self._api.knowledge_train_stop(request)
