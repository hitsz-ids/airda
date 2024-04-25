import json
import logging
from typing import AsyncGenerator

from fastapi.responses import JSONResponse, StreamingResponse
from overrides import override

from airda.agent.agent import DataAgent
from airda.agent.data_agent_context import DataAgentContext
from airda.agent.planner.data_agent_planner_params import DataAgentPlannerParams
from airda.server.api import API
from airda.server.protocol import (
    ChatCompletionRequest,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    DeltaMessage,
    ErrorResponse,
)

logger = logging.getLogger(__name__)


class APIImpl(API):
    _cache: dict[str, StreamingResponse] = {}
    agent: DataAgentContext

    def __init__(self):
        super().__init__()
        self.agent = DataAgent().run()

    @override
    async def create_completion(self, request: ChatCompletionRequest):
        async def stream_generator() -> AsyncGenerator[str, None]:
            try:
                pipeline = self.agent.get_planner().plan(DataAgentPlannerParams(**vars(request)))
                async for item in pipeline.execute():
                    yield f"data: {make_stream_data(content=item)}\n\n"
            except Exception as e:
                print(e)

        return StreamingResponse(stream_generator(), media_type="text/event-stream")


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
