import fastapi
from fastapi import BackgroundTasks, Depends, File, Form, UploadFile
from overrides import overrides

from sql_agent.framework import WebFrameworkServer
from sql_agent.protocol import (
    ChatCompletionRequest,
    CompletionInstructionSyncRequest,
    CompletionKnowledgeLoadRequest,
)


async def upload_file_form(
    file: UploadFile = File(...), file_id: str = Form(...), file_name: str = Form(...)
):
    return CompletionKnowledgeLoadRequest(file=file, file_id=file_id, file_name=file_name)


class FastAPIServer(WebFrameworkServer):
    def __init__(self, host="0.0.0.0", port=8080):
        super().__init__(host, port)
        self.router = None

    @overrides
    def create_app(self):
        return fastapi.FastAPI(debug=True)

    @overrides
    def run_server(self):
        self.add_routes(self.app)
        import uvicorn

        uvicorn.run(self.app, host=self.host, port=self.port)

    @overrides
    def add_routes(self, app):
        self.router = fastapi.APIRouter()
        self.router.add_api_route(
            "/v1/chat/completions",
            self.create_completion,
            methods=["POST"],
            tags=["chat completions"],
        )
        self.router.add_api_route(
            "/v1/instruction/sync",
            self.instruction_sync,
            methods=["POST"],
            tags=["add gold_sql"],
        )
        self.router.add_api_route(
            "/v1/knowledge/train",
            self.knowledge_train,
            methods=["POST"],
            tags=["knowledge train"],
        )

        self.app.include_router(self.router)

    async def create_completion(self, request: ChatCompletionRequest):
        return await self._api.create_completion(request)

    async def instruction_sync(
        self, request: CompletionInstructionSyncRequest, background_tasks: BackgroundTasks
    ):
        return await self._api.instruction_sync(request, background_tasks)

    async def knowledge_train(
        self,
        background_tasks: BackgroundTasks,
        request: CompletionKnowledgeLoadRequest = Depends(upload_file_form),
    ):
        await self._api.knowledge_train(request, background_tasks)
