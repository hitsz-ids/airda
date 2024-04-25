from abc import abstractmethod
from typing import AsyncGenerator, Generic, List, TypeVar

from airda.framework.agent.context import Context
from airda.framework.agent.module.assistant_manager.assistant.assistant import (
    Assistant,
)

from .pipeline_params import PipelineParams
from .pipline_result import PipelineResult

PR = TypeVar("PR", bound=PipelineResult)
PP = TypeVar("PP", bound=PipelineParams)


class Pipeline(Generic[PP, PR]):
    steps: List[type(Assistant)]
    assistants: dict[type(Assistant), Assistant] = {}
    params: PP
    context: Context

    def __init__(self, params: PP, context: Context):
        self.params = params
        self.context = context
        self.steps = self.init()

    @abstractmethod
    def init(self) -> List[type(Assistant)]:
        pass

    @abstractmethod
    def start(self, assistant: type[Assistant]) -> Assistant:
        pass

    @abstractmethod
    def end(self, assistant: Assistant):
        pass

    async def execute(self) -> AsyncGenerator[PR, None]:
        for step in self.steps:
            assistant = self.start(step)
            self.assistants[step] = assistant
            async for item in assistant.run():
                yield item
            self.end(assistant)
