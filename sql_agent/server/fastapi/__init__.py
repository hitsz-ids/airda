import os

import fastapi
from fastapi import BackgroundTasks
from fastapi import FastAPI as _FastAPI
from fastapi.routing import APIRoute
import sql_agent
from sql_agent.config import Settings
from sql_agent.protocol import (
    ChatCompletionRequest,
    CompletionKnowledgeLoadRequest,
    CompletionKnowledgeDeleteRequest,
    CompletionGoldenSQLAddRequest
)


def use_route_names_as_operation_ids(app: _FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.
    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


class FastAPI(sql_agent.server.Server):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._app = fastapi.FastAPI(debug=True)
        self._api: sql_agent.api.API = sql_agent.client(settings)

        self.router = fastapi.APIRouter()

        self.router.add_api_route(
            "/v1/chat/completions",
            self.create_completion,
            methods=["POST"],
            tags=["chat completions"],
        )

        self.router.add_api_route(
            "/v1/knowledge/train",
            self.knowledge_train,
            methods=["POST"],
            tags=["knowledge train"],
        )

        self.router.add_api_route(
            "/v1/knowledge/train/delete",
            self.delete_knowledge_file,
            methods=["POST"],
            tags=["delete knowledge"],
        )

        self.router.add_api_route(
            "/v1/gold_sql/add",
            self.add_gold_sql,
            methods=["POST"],
            tags=["add gold_sql"],
        )

        self._app.include_router(self.router)
        use_route_names_as_operation_ids(self._app)

    def app(self) -> fastapi.FastAPI:
        return self._app

    async def create_completion(self, request: ChatCompletionRequest):
        return await self._api.create_completion(request)

    async def knowledge_train(self, request: CompletionKnowledgeLoadRequest, background_tasks: BackgroundTasks):
        await self._api.knowledge_train(request, background_tasks)

    def delete_knowledge_file(self, request: CompletionKnowledgeDeleteRequest):
        return self._api.delete_knowledge_file(request)

    async def add_gold_sql(self, request: CompletionGoldenSQLAddRequest):
        return self._api.add_golden_sql(request)
