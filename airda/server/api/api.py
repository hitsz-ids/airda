import json
import logging
from typing import AsyncGenerator

from fastapi.responses import JSONResponse, StreamingResponse
from overrides import overrides

from airda.agent.agent import DataAgent
from airda.agent.data_agent_context import DataAgentContext
from airda.agent.exception.already_exists_error import AlreadyExistsError
from airda.agent.planner.data_agent_planner_params import DataAgentPlannerParams
from airda.agent.storage import StorageKey
from airda.agent.storage.entity.datasource import Datasource, Kind
from airda.agent.storage.repositories.datasource_repository import DatasourceRepository
from airda.server.api import API
from airda.server.protocol import (
    AddDatasourceRequest,
    ChatCompletionRequest,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    DeltaMessage,
    ErrorResponse,
)

logger = logging.getLogger(__name__)


class APIImpl(API):
    _cache: dict[str, StreamingResponse] = {}
    context: DataAgentContext

    def __init__(self):
        super().__init__()
        self.context = DataAgent().run()

    @overrides
    async def create_completion(self, request: ChatCompletionRequest):
        async def stream_generator() -> AsyncGenerator[str, None]:
            try:
                pipeline = self.context.get_planner().plan(DataAgentPlannerParams(**vars(request)))
                async for item in pipeline.execute():
                    yield f"data: {make_stream_data(content=item)}\n\n"
            except Exception as e:
                print(e)

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    @overrides
    def add_datasource(self, request: AddDatasourceRequest):
        kind = Kind.getKind(request.kind)
        if kind is None:
            # output_colored_text(f"不支持的数据源类型[{kind}], PS: 支持类型: [{Kind.MYSQL.value}]", "error")
            message = f"不支持的数据源类型[{kind}], PS: 支持类型: [{Kind.MYSQL.value}]"
            return JSONResponse(ErrorResponse(message=message, code=-1).dict())
        datasource_repository = self.context.get_repository(StorageKey.DATASOURCE).convert(
            DatasourceRepository
        )
        try:
            datasource_repository.add(
                Datasource(
                    name=request.name,
                    host=request.host,
                    port=request.port,
                    database=request.database,
                    kind=kind,
                    username=request.username,
                    password=request.password,
                )
            )
            # output_colored_text("执行成功", "success")
        except AlreadyExistsError:
            pass
            # output_colored_text(f"执行失败, [{name}]数据源已存在", "error")


def make_stream_data(
    content: str | dict | list,
    rep_type: str = "stream",
    model: str = "gpt-4-1106-preview",
    finish_reason: str = "",
    session_id: str = "",
):
    push_json = {"type": rep_type, "data": content}
    choice_data = ChatCompletionResponseStreamChoice(
        index=1,
        delta=DeltaMessage(
            role="assistant_manager",
            content=json.dumps(push_json, ensure_ascii=False),
            finish_reason=finish_reason,
        ),
    )
    chunk = ChatCompletionStreamResponse(id=session_id, choices=[choice_data], model=model)
    return chunk.json(exclude_unset=True)


def create_error_response(code: int, message: str) -> JSONResponse:
    return JSONResponse(ErrorResponse(message=message, code=code).dict(), status_code=400)
